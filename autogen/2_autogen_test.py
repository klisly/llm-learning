
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
    system_message="Your name is Cathy and you are a part of a duo of comedians.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",  # Never ask for human input.
)

joe = ConversableAgent(
    "joe",
    system_message="Your name is Joe and you are a part of a duo of comedians.",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",  # Never ask for human input.
)

result = joe.initiate_chat(cathy, message="Cathy, tell me a joke.", max_turns=2)

