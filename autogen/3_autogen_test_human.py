
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
import os
from autogen import ConversableAgent

agent_with_number = ConversableAgent(
    "agent_with_number",
    system_message="You are playing a game of guess-my-number. You have the "
    "number 53 in your mind, and I will try to guess it. "
    "If I guess too high, say 'too high', if I guess too low, say 'too low'. ",
    llm_config={"config_list": config_list},
    is_termination_msg=lambda msg: "53" in msg["content"],  # terminate if the number is guessed by the other agent
    human_input_mode="NEVER",  # never ask for human input
)

# 无人类介入
# agent_guess_number = ConversableAgent(
#     "agent_guess_number",
#     system_message="I have a number in my mind, and you will try to guess it. "
#     "If I say 'too high', you should guess a lower number. If I say 'too low', "
#     "you should guess a higher number. ",
#     llm_config={"config_list": config_list},
#     # human_input_mode="NEVER",
# )

# result = agent_with_number.initiate_chat(
#     agent_guess_number,
#     message="I have a number between 1 and 100. Guess it!",
# )

#有人类介入
# human_proxy = ConversableAgent(
#     "human_proxy",
#     llm_config=False,  # no LLM used for human proxy
#     human_input_mode="ALWAYS",  # always ask for human input
# )

# # Start a chat with the agent with number with an initial guess.
# result = human_proxy.initiate_chat(
#     agent_with_number,  # this is the same agent with the number as before
#     message="10",
# )

# 终止后介入
agent_with_number = ConversableAgent(
    "agent_with_number",
    system_message="You are playing a game of guess-my-number. "
    "In the first game, you have the "
    "number 53 in your mind, and I will try to guess it. "
    "If I guess too high, say 'too high', if I guess too low, say 'too low'. ",
    llm_config={"config_list": config_list},
    max_consecutive_auto_reply=1,  # maximum number of consecutive auto-replies before asking for human input
    is_termination_msg=lambda msg: "53" in msg["content"],  # terminate if the number is guessed by the other agent
    human_input_mode="TERMINATE",  # ask for human input until the game is terminated
)

agent_guess_number = ConversableAgent(
    "agent_guess_number",
    system_message="I have a number in my mind, and you will try to guess it. "
    "If I say 'too high', you should guess a lower number. If I say 'too low', "
    "you should guess a higher number. ",
    llm_config={"config_list": config_list},
    human_input_mode="NEVER",
)

result = agent_with_number.initiate_chat(
    agent_guess_number,
    message="I have a number between 1 and 100. Guess it!",
)