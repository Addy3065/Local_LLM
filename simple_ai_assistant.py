#standard library import 
import os       # default downloaded package in python 

#third party libraries 
from openai import OpenAI # package 1 
from dotenv import load_dotenv      # package 2 

#local modules 
from tools import TOOLS ,run_tool
from Utilities.utilities import log 



load_dotenv()
# by defualt looks for the env file and load its variable 


client =OpenAI(
    base_url=os.getenv("BASE_URL"),       # ollama server 
    api_key=os.getenv("API_KEY")         #ollama doesnt need key 
)
messages=[]

# safety limit : the max number of tool calls for one question
max_steps=5 

# system_command=input("enter instruction for system")
messages.append(
    {
        "role": "system",
        "content": "Respond within 20 words "
    }
)

#chat loop starts 
while True: 
    user_input=input("\n addy: ")
    if user_input.lower() in ["stop","exit","bye","quit"]:
        break
    messages.append(
        {
            "role":"user",
            "content": user_input
        }
    )
    
 
    #sequential tool calling  with max_steps
    for step in range(max_steps):
        response = client.chat.completions.create(
             model=os.getenv("MODEL"),
             messages=messages,
             tools=TOOLS,
         )
        msg=response.choices[0].message   

        if not msg.tool_calls:
            break

        log(f"step {step+1}: model requested {len(msg.tool_calls)} tools")
        messages.append(msg)
        
        #for loop for all tools required by LLM 
        for tool_call in msg.tool_calls:
            result =run_tool(tool_call)
           # appending tool response to messages 
            messages.append(
                {
                    "role":"tool",
                    "tool_id":tool_call.id,
                    "content":str(result)       # type casting 
                }
            )
    #"else" agaisnt for loop runs when the for loop is completely executed         
    else:
        fallback="Sorry, the tool limit exhausted and response could not be generates"
        messages.append({
            "role":"assistant",
            "content":fallback
        })
        print("Assistant: "+ fallback)
        continue    # ask user for another prompt 


    messages.append(
        {
            "role":"assistant",
            "content":msg.content
        }
    )
    print("Assistant: "+ (msg.content or ""))