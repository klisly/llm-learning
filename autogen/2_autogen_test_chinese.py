
from autogen import ConversableAgent
'''
双人对话
'''

config_list = [ 
        { 
            "model": "Qwen-7B-Chat-Int4", 
            "base_url": "http://localhost:8000/v1", 
            "api_type": "open_ai", 
            "api_key": "NULL", # just a placeholder 
        } 
    ]


cathy = ConversableAgent(
    "cathy",
    system_message="你的名字是多多，你是男生，你是少少的男朋友",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",  # Never ask for human input.
)

joe = ConversableAgent(
    "joe",
    system_message="你的名字是少少，你是女生，你是多多的女朋友。",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",  # Never ask for human input.
)

# max_turns 最大轮次
# max_consecutive_auto_reply 最大连续几次回复

result = joe.initiate_chat(cathy, message="多多, 我们相互写情书吧.你先写一封", max_turns=3)

