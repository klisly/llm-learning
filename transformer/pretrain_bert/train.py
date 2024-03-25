import argparse
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer, RobertaForMaskedLM, AdamW
from tqdm import tqdm

# 1. 定义数据集类
class TextDataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length=510):
        self.data = []
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.max_text_length = 0  # 保存最长文本的长度
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                self.data.append(line.strip())
                if max_length is None:
                    self.max_text_length = max(self.max_text_length, len(line.split()))  # 更新最长文本的长度

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        encoded_text = self.tokenizer.encode_plus(
            self.data[idx:idx+1],
            max_length=self.max_length,
            model_max_lenght = self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        # print(encoded_text['input_ids'][0].shape, encoded_text['attention_mask'][0].shape)
        return encoded_text['input_ids'][0], encoded_text['attention_mask'][0]

def train_roberta_model(file_path, model_out, num_train_epochs=3):
    # 2. 加载预训练的RoBERTa模型和tokenizer
    model_name = 'roberta-base'
    tokenizer = RobertaTokenizer.from_pretrained(model_name)
    model = RobertaForMaskedLM.from_pretrained(model_name)

    # 3. 准备数据集
    dataset = TextDataset(file_path, tokenizer)

    # 4. 设置训练参数
    optimizer = AdamW(model.parameters(), lr=5e-5)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 5. 训练模型
    model.to(device)
    model.train()
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)
    
    for epoch in range(num_train_epochs):
        total_loss = 0
        progress_bar = tqdm(enumerate(dataloader), total=len(dataloader))
        for step, batch in enumerate(progress_bar):
            input_ids, attention_mask = batch[1]
            input_ids = input_ids.to(device)
            attention_mask = attention_mask.to(device)
            optimizer.zero_grad()

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
            loss = outputs.loss
            total_loss += loss.item()
            loss.backward()
            optimizer.step()
            progress_bar.set_description(f"Epoch {epoch+1}/{num_train_epochs} - Loss: {total_loss / (step + 1):.4f}")


    # 6. 保存模型
    model.save_pretrained(model_out)
    tokenizer.save_pretrained(model_out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train RoBERTa model based on a given text corpus.")
    parser.add_argument("--path", type=str, default='/home/nakai/project/aigc/llm/learning/transformer/pretrain_bert/10000_chat_corpus.txt', help="Path to the text corpus file")
    parser.add_argument("--model-out", type=str, default='/home/nakai/project/aigc/llm/learning/transformer/pretrain_bert/output_model', help="Output directory for the trained model")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    args = parser.parse_args()

    train_roberta_model(args.path, args.model_out, args.epochs)
