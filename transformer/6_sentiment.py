import os
import random
import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoConfig
from transformers import BertPreTrainedModel, BertModel
from transformers.activations import ACT2FN
from transformers import AdamW, get_scheduler
from sklearn.metrics import classification_report
from tqdm.auto import tqdm

vtype = 'base'
max_length = 512
batch_size = 4
learning_rate = 1e-5
epoch_num = 3

def seed_everything(seed=1029):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True

def get_prompt(x):
    prompt = f'总体上来说很[MASK]。{x}'
    return {
        'prompt': prompt, 
        'mask_offset': prompt.find('[MASK]')
    }

def get_verbalizer(tokenizer, vtype):
    assert vtype in ['base', 'virtual']
    return {
        'pos': {'token': '好', 'id': tokenizer.convert_tokens_to_ids("好")}, 
        'neg': {'token': '差', 'id': tokenizer.convert_tokens_to_ids("差")}
    } if vtype == 'base' else {
        'pos': {
            'token': '[POS]', 'id': tokenizer.convert_tokens_to_ids("[POS]"), 
            'description': '好的、优秀的、正面的评价、积极的态度'
        }, 
        'neg': {
            'token': '[NEG]', 'id': tokenizer.convert_tokens_to_ids("[NEG]"), 
            'description': '差的、糟糕的、负面的评价、消极的态度'
        }
    }

seed_everything(12)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Using {device} device')

class ChnSentiCorp(Dataset):
    def __init__(self, data_file):
        self.data = self.load_data(data_file)
    
    def load_data(self, data_file):
        Data = {}
        # 打开文件，以utf-8编码读取文件内容
        with open(data_file, 'rt', encoding='utf-8') as f:
# 遍历文件中的每一行
            for idx, line in enumerate(f):
# 将每一行按制表符分割，获取每一行的两个元素
                items = line.strip().split('\t')
# 断言，确保每一行有且只有两个元素
                assert len(items) == 2
# 调用get_prompt函数，获取prompt和mask_offset
                prompt_data = get_prompt(items[0])
# 将获取的prompt、mask_offset和label添加到Data字典中
                Data[idx] = {
                    'prompt': prompt_data['prompt'], 
                    'mask_offset': prompt_data['mask_offset'], 
                    'label': items[1]
                }
        return Data
    
    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

train_data = ChnSentiCorp('data/chnsenticorp/train/part.0')
valid_data = ChnSentiCorp('data/chnsenticorp/dev/part.0')
test_data = ChnSentiCorp('data/chnsenticorp/test/part.0')

checkpoint = "bert-base-chinese"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
if vtype == 'virtual':
    tokenizer.add_special_tokens({'additional_special_tokens': ['[POS]', '[NEG]']})

verbalizer = get_verbalizer(tokenizer, vtype=vtype)
pos_id, neg_id = verbalizer['pos']['id'], verbalizer['neg']['id']

# 定义collote_fn函数，用于处理batch_samples
def collote_fn(batch_samples):
    # 初始化batch_sentences、batch_mask_idxs、batch_labels三个列表
    batch_sentences, batch_mask_idxs, batch_labels  = [], [], []
    # 遍历batch_samples中的每一个sample
    for sample in batch_samples:
        # 将sample中的prompt添加到batch_sentences中
        batch_sentences.append(sample['prompt'])
        # 使用tokenizer对prompt进行编码
        encoding = tokenizer(sample['prompt'], truncation=True)
        # 获取sample中的mask_offset
        mask_idx = encoding.char_to_token(sample['mask_offset'])
        # 断言mask_idx不为空
        assert mask_idx is not None
        # 将mask_idx添加到batch_mask_idxs中
        batch_mask_idxs.append(mask_idx)
        # 将sample中的label添加到batch_labels中
        batch_labels.append(int(sample['label']))
    # 使用tokenizer对batch_sentences进行编码，并返回batch_inputs
    batch_inputs = tokenizer(
        batch_sentences, 
        max_length=max_length, 
        padding=True, 
        truncation=True, 
        return_tensors="pt"
    )
    # 初始化label_word_id
    label_word_id = [neg_id, pos_id]
    # 返回batch_inputs、batch_mask_idxs、label_word_id、batch_labels
    return {
        'batch_inputs': batch_inputs, 
        'batch_mask_idxs': batch_mask_idxs, 
        'label_word_id': label_word_id, 
        'labels': batch_labels
    }
train_dataloader = DataLoader(train_data, batch_size=batch_size, shuffle=True, collate_fn=collote_fn)
valid_dataloader = DataLoader(valid_data, batch_size=batch_size, shuffle=False, collate_fn=collote_fn)
test_dataloader = DataLoader(test_data, batch_size=batch_size, shuffle=False, collate_fn=collote_fn)

# 定义一个函数，用于在输入张量input中，按照维度dim和索引index进行索引选择
def batched_index_select(input, dim, index):
    '''
    :param input: torch.Size([B, C, N])
    :param dim: 维度
    :param index: torch.Size([B, M])
    :return: torch.Size([B, M, C])
    '''
    # 遍历输入张量的维度
    for i in range(1, len(input.shape)):
        # 如果当前维度不是dim，则将index添加当前维度
        if i != dim:
            index = index.unsqueeze(i)
    # 计算输出张量的形状
    expanse = list(input.shape)
    expanse[0] = -1
    expanse[dim] = -1
    # 将index扩展到输出张量的形状
    index = index.expand(expanse)
    # 返回输出张量
    return torch.gather(input, dim, index)

class BertPredictionHeadTransform(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.dense = nn.Linear(config.hidden_size, config.hidden_size)
        if isinstance(config.hidden_act, str):
            self.transform_act_fn = ACT2FN[config.hidden_act]
        else:
            self.transform_act_fn = config.hidden_act
        self.LayerNorm = nn.LayerNorm(config.hidden_size, eps=config.layer_norm_eps)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.dense(hidden_states)
        hidden_states = self.transform_act_fn(hidden_states)
        hidden_states = self.LayerNorm(hidden_states)
        return hidden_states

class BertLMPredictionHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.transform = BertPredictionHeadTransform(config)
        self.decoder = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        self.bias = nn.Parameter(torch.zeros(config.vocab_size))
        self.decoder.bias = self.bias

    def forward(self, hidden_states):
        hidden_states = self.transform(hidden_states)
        hidden_states = self.decoder(hidden_states)
        return hidden_states

class BertOnlyMLMHead(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.predictions = BertLMPredictionHead(config)

    def forward(self, sequence_output: torch.Tensor) -> torch.Tensor:
        prediction_scores = self.predictions(sequence_output)
        return prediction_scores

class BertForPrompt(BertPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.bert = BertModel(config, add_pooling_layer=False)
        self.cls = BertOnlyMLMHead(config)
        # Initialize weights and apply final processing
        self.post_init()
    
    def get_output_embeddings(self):
        return self.cls.predictions.decoder

    def set_output_embeddings(self, new_embeddings):
        self.cls.predictions.decoder = new_embeddings
    
    def forward(self, batch_inputs, batch_mask_idxs, label_word_id, labels=None):
        bert_output = self.bert(**batch_inputs)
        sequence_output = bert_output.last_hidden_state
        batch_mask_reps = batched_index_select(sequence_output, 1, batch_mask_idxs.unsqueeze(-1)).squeeze(1)
        pred_scores = self.cls(batch_mask_reps)[:, label_word_id]

        loss = None
        if labels is not None:
            loss_fn = nn.CrossEntropyLoss()
            loss = loss_fn(pred_scores, labels)
        return loss, pred_scores

config = AutoConfig.from_pretrained(checkpoint)
model = BertForPrompt.from_pretrained(checkpoint, config=config).to(device)
if vtype == 'virtual':
    model.resize_token_embeddings(len(tokenizer))
    print(f"initialize embeddings of {verbalizer['pos']['token']} and {verbalizer['neg']['token']}")
    with torch.no_grad():
        pos_tokenized = tokenizer(verbalizer['pos']['description'])
        pos_tokenized_ids = tokenizer.convert_tokens_to_ids(pos_tokenized)
        neg_tokenized = tokenizer(verbalizer['neg']['description'])
        neg_tokenized_ids = tokenizer.convert_tokens_to_ids(neg_tokenized)
        new_embedding = model.bert.embeddings.word_embeddings.weight[pos_tokenized_ids].mean(axis=0)
        model.bert.embeddings.word_embeddings.weight[pos_id, :] = new_embedding.clone().detach().requires_grad_(True)
        new_embedding = model.bert.embeddings.word_embeddings.weight[neg_tokenized_ids].mean(axis=0)
        model.bert.embeddings.word_embeddings.weight[neg_id, :] = new_embedding.clone().detach().requires_grad_(True)
  
def to_device(batch_data):
    new_batch_data = {}
    for k, v in batch_data.items():
        if k == 'batch_inputs':
            new_batch_data[k] = {
                k_: v_.to(device) for k_, v_ in v.items()
            }
        elif k == 'label_word_id':
            new_batch_data[k] = v
        else:
            new_batch_data[k] = torch.tensor(v).to(device)
    return new_batch_data

def train_loop(dataloader, model, optimizer, lr_scheduler, epoch, total_loss):
    progress_bar = tqdm(range(len(dataloader)))
    progress_bar.set_description(f'loss: {0:>7f}')
    finish_batch_num = epoch * len(dataloader)
    
    model.train()
    for step, batch_data in enumerate(dataloader, start=1):
        batch_data = to_device(batch_data)
        outputs = model(**batch_data)
        loss = outputs[0]

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        lr_scheduler.step()

        total_loss += loss.item()
        progress_bar.set_description(f'loss: {total_loss/(finish_batch_num + step):>7f}')
        progress_bar.update(1)
    return total_loss

# 定义一个函数test_loop，用于测试dataloader和model
def test_loop(dataloader, model):
    # 定义一个列表true_labels，用于存储真实标签
    true_labels, predictions = [], []
    # 将model设置为评估模式
    model.eval()
    # 使用torch.no_grad()禁止梯度计算
    with torch.no_grad():
        # 遍历dataloader中的每一个batch_data
        for batch_data in tqdm(dataloader):
            # 将真实标签添加到true_labels中
            true_labels += batch_data['labels']
            # 将batch_data中的数据移动到设备中
            batch_data = to_device(batch_data)
            # 使用model对batch_data进行预测
            outputs = model(**batch_data)
            # 获取预测结果
            pred = outputs[1]
            # 将预测结果添加到predictions中
            predictions += pred.argmax(dim=-1).cpu().numpy().tolist()
    # 使用classification_report函数计算分类报告，并将结果以字典的形式存储
    metrics = classification_report(true_labels, predictions, output_dict=True)
    # 获取正样本的准确率、召回率和F1值
    pos_p, pos_r, pos_f1 = metrics['1']['precision'], metrics['1']['recall'], metrics['1']['f1-score']
    # 获取负样本的准确率、召回率和F1值
    neg_p, neg_r, neg_f1 = metrics['0']['precision'], metrics['0']['recall'], metrics['0']['f1-score']
    # 获取宏平均F1值和微平均F1值
    macro_f1, micro_f1 = metrics['macro avg']['f1-score'], metrics['weighted avg']['f1-score']
    # 打印正样本的准确率、召回率和F1值
    print(f"pos: {pos_p*100:>0.2f} / {pos_r*100:>0.2f} / {pos_f1*100:>0.2f}, neg: {neg_p*100:>0.2f} / {neg_r*100:>0.2f} / {neg_f1*100:>0.2f}")
    # 打印宏平均F1值和微平均F1值
    print(f"Macro-F1: {macro_f1*100:>0.2f} Micro-F1: {micro_f1*100:>0.2f}\n")
    # 返回分类报告
    return metrics

optimizer = AdamW(model.parameters(), lr=learning_rate)
lr_scheduler = get_scheduler(
    "linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=epoch_num*len(train_dataloader),
)

total_loss = 0.
best_f1_score = 0.
for epoch in range(epoch_num):
    print(f"Epoch {epoch+1}/{epoch_num}\n" + 30 * "-")
    total_loss = train_loop(train_dataloader, model, optimizer, lr_scheduler, epoch, total_loss)
    valid_scores = test_loop(valid_dataloader, model)
    macro_f1, micro_f1 = valid_scores['macro avg']['f1-score'], valid_scores['weighted avg']['f1-score']
    f1_score = (macro_f1 + micro_f1) / 2
    if f1_score > best_f1_score:
        best_f1_score = f1_score
        print('saving new weights...\n')
        torch.save(
            model.state_dict(), 
            f'epoch_{epoch+1}_valid_macrof1_{(macro_f1*100):0.3f}_microf1_{(micro_f1*100):0.3f}_model_weights.bin'
        )
print("Done!")