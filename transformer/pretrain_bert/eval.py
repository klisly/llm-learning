from transformers import RobertaTokenizer, RobertaForMaskedLM
import random
import torch

# 随机MASK测试
def random_mask_test(model, tokenizer, text_corpus, num_samples=1000):
    # 从语料库中随机选择num_samples条文本
    samples = random.sample(text_corpus, num_samples)

    # 遍历每条文本进行随机MASK测试
    total_correct = 0
    total_words = 0
    for sample in samples:
        # 随机选择一些词进行MASK
        tokens = tokenizer.tokenize(sample, )
        num_tokens = min(len(tokens), 510)
        masked_indices = random.sample(range(num_tokens), min(5, num_tokens))  # 最多MASK 5个词
        for index in masked_indices:
            masked_token = tokens[index]
            tokens[index] = '[MASK]'
            masked_text = ' '.join(tokens)
            
            # 使用模型预测MASK位置的词

            input_ids = tokenizer.encode_plus(
                masked_text,
                max_length=512,
                padding='max_length',
                truncation=True,
                return_tensors='pt'
            )
            with torch.no_grad():
                outputs = model(input_ids=input_ids['input_ids'])
                tmp = outputs['logits'][0]
                predictions = tmp.argmax(dim=-1).squeeze().tolist()
            
            # 获取预测结果并计算正确预测的数量
            predicted_token = tokenizer.decode([predictions[index]])
            print(tokens, predicted_token, masked_token)
            if predicted_token == masked_token:
                total_correct += 1
            total_words += 1
    
    # 计算准确率
    accuracy = total_correct / total_words
    return accuracy

# 在模型上执行随机MASK测试并计算准确率
def evaluate(model, tokenizer, text_corpus, num_samples=1000):
    model.eval()
    accuracy = random_mask_test(model, tokenizer, text_corpus, num_samples)
    print(f"Random MASK test accuracy: {accuracy:.2%}")

# # 使用示例
# # model 和 tokenizer 是预训练的RoBERTa模型和tokenizer
# # text_corpus 是语料库，即文本语料文件中的所有文本
# evaluate(model, tokenizer, text_corpus, num_samples=1000)

def load_corpus(file_path):
    corpus = []
    with open(file_path) as f:
        corpus = f.readlines()
    return corpus

items = load_corpus('/data2/project/aigc/llm/learning/transformer/pretrain_bert/tmp.txt')

model_name = '/home/nakai/project/aigc/llm/learning/transformer/pretrain_bert/all_robert_model'
model_name = 'roberta-base'
tokenizer = RobertaTokenizer.from_pretrained(model_name)
model = RobertaForMaskedLM.from_pretrained(model_name)

evaluate(model, tokenizer, items, num_samples=3)


model_name = 'roberta-base'

model_name = '/home/nakai/project/aigc/llm/learning/transformer/pretrain_bert/all_robert_model'

predict_mask = pipeline(
    'fill-mask',
    model=model_name,
    tokenizer=model_name
)


predict_mask('你之前谈恋爱都是<mask>的吗')