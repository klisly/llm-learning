import torch
from transformers import RobertaTokenizer, RobertaForMaskedLM
from torch.utils.data import DataLoader
import numpy as np

# 1. 加载预训练的RoBERTa模型和tokenizer
model_name = 'roberta-base'  # 使用预训练的roberta-base模型
tokenizer = RobertaTokenizer.from_pretrained(model_name)
model = RobertaForMaskedLM.from_pretrained(model_name)

# 2. 准备数据
# 示例数据
texts = ["This is a sentence.", "Another example sentence.", "And one more sentence."]
encoded_texts = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

# 3. 训练参数设置
optimizer = torch.optim.AdamW(model.parameters(), lr=5e-5)

# 4. 训练模型
num_epochs = 3
for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    for text in encoded_texts['input_ids']:
        optimizer.zero_grad()
        output = model(text.unsqueeze(0), labels=text.unsqueeze(0))
        loss = output.loss
        total_loss += loss.item()
        loss.backward()
        optimizer.step()
    print("Epoch {} - Average Loss: {}".format(epoch + 1, total_loss / len(encoded_texts['input_ids'])))

# 5. 保存模型
output_dir = "./trained_roberta_model"
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
