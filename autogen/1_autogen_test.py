
from autogen import ConversableAgent
'''
单人对话
'''

# config_list = [ 
#         { 
#             "model": "Qwen-7B-Chat-Int4", 
#             "base_url": "http://localhost:8000/v1", 
#             "api_type": "open_ai", 
#             "api_key": "NULL", # just a placeholder 
#         } 
#     ]


import os
os.environ['OPENAI_API_KEY'] = 'sk-cbb956b0324648ca850d519fb4a8906585571044a24ceae7'
os.environ["OPENAI_BASE_URL"] = "https://www.xiaoerchaoren.com:8907/g/v1"
config_list = [{"model": "gpt-4", "api_key": os.environ.get("OPENAI_API_KEY")}]

agent = ConversableAgent(
    "chatbot",
    llm_config={"config_list": config_list},
    code_execution_config=False,  # Turn off code execution, by default it is off.
    function_map=None,  # No registered functions, by default it is None.
    human_input_mode="NEVER",  # Never ask for human input.
)

reply = agent.generate_reply(messages=[{"content": "你是谁", "role": "user"}])
print(reply)