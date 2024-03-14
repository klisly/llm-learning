from transformers import BertModel

model = BertModel.from_pretrained("bert-base-cased")

# 分词策略
print("按词、按字符、按子词")
tokenized_text = "Jim Henson was a puppeteer".split()
print(tokenized_text)


from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

sequence = "Using a Transformer network is simple"
tokens = tokenizer.tokenize(sequence)

print(tokens)

print("encode:")
sequence_ids = tokenizer.encode(sequence)

print(sequence_ids)

print("decode:")
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")

decoded_string = tokenizer.decode([7993, 170, 11303, 1200, 2443, 1110, 3014])
print(decoded_string)

decoded_string = tokenizer.decode([101, 7993, 170, 13809, 23763, 2443, 1110, 3014, 102])
print(decoded_string)