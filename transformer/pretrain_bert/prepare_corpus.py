import argparse
import pandas as pd
from tqdm import tqdm

def combine_conversations(csv_path, row_limit=None, out_path='combined_conversations.txt'):
    # 读取CSV文件
    df = pd.read_csv(csv_path, nrows=row_limit)

    # 创建一个字典来存储属于同两个人的对话消息
    conversations = {}

    # 将消息组合成长文本
    for _, row in tqdm(df.iterrows()):
        from_uid = row['src_id']
        to_uid = row['dest_id']
        msg = str(row['content'])
        
        # 将from_uid和to_uid按照字母顺序组合成一个元组，确保对话参与者的组合是唯一的
        participants = tuple(sorted([from_uid, to_uid]))
        
        if participants not in conversations:
            conversations[participants] = []
        if msg.startswith("{"):
            continue
        conversations[participants].append(msg)

    # 将组合后的消息写入文件
    with open(out_path, 'w', encoding='utf-8') as f:
        for participants, msgs in conversations.items():
            def join_msgs(msgs):
                result = []
                current_msg = ''
                for msg in msgs:
                    if len(current_msg) + len(msg) <= 512:
                        current_msg += "。"+msg
                    else:
                        result.append(current_msg)
                        current_msg = msg
                result.append(current_msg)
                return result
            sub_msgs= join_msgs(msgs)
            for sub_msg in sub_msgs:
                sub_msg = sub_msg.strip()
                if len(sub_msg) > 0:
                    f.write(sub_msg + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine messages from the same two users in a CSV file.")
    parser.add_argument("path", type=str, help="Path to the CSV file")
    parser.add_argument("--row", type=int, default=None, help="Number of rows to process")
    parser.add_argument("--out_path", type=str, default="combined_conversations.txt", help="Output file path")
    args = parser.parse_args()

    combine_conversations(args.path, args.row, args.out_path)

