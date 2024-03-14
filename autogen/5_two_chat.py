import os
from autogen import ConversableAgent
config_list = [ 
        { 
            "model": "Qwen-7B-Chat-Int4", 
            "base_url": "http://localhost:8000/v1", 
            "api_type": "open_ai", 
            "api_key": "NULL", # just a placeholder 
        } 
    ]
student_agent = ConversableAgent(
    name="Student_Agent",
    system_message="You are a student willing to learn.",
    llm_config={"config_list": config_list},
)
teacher_agent = ConversableAgent(
    name="Teacher_Agent",
    system_message="You are a math teacher.",
    llm_config={"config_list": config_list},
)

chat_result = student_agent.initiate_chat(
    teacher_agent,
    message="What is triangle inequality?",
    summary_method="reflection_with_llm",
    max_turns=4,
)

# Get the chat history.
import pprint

pprint.pprint(chat_result.chat_history)
pprint.pprint(chat_result.summary)

