#standard library import 
import os       # default downloaded package in python 
from types import SimpleNamespace

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

def stream_chat(history):
    stream=client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=history,
        tools=TOOLS,
        stream=True
    )
    full_response="" 
    calls={}
    label_prinited=False

    try:
        for chunk in stream:
            if not chunk.choices:
                continue

            #Content Streaming
            delta=chunk.choices[0].delta
            if delta.content:
                if label_prinited==False:
                    print("Assistant: ",end="",flush=True)
                    label_prinited=True
                print(delta.content,end="",flush=True)
                full_response+=delta.content
                
            #Tool Calls
            for tc in (delta.tool_calls or []):     # for loop skips is delta.tool call is undefined 
                obj = calls.setdefault(
                    tc.index,
                    SimpleNamespace(id=None, function=SimpleNamespace(name="", arguments="")),
                )
                if tc.id:
                    obj.id = tc.id
                if tc.function and tc.function.name:
                    obj.function.name += tc.function.name
                if tc.function and tc.function.arguments:
                    obj.function.arguments += tc.function.arguments
    except KeyboardInterrupt:
        print("Interupted")
        calls={}
    
    if label_prinited:
        print()
    calls_list=[]
    for key in sorted(calls):
        calls_list.append(calls[key])


    return full_response,calls_list

def build_tool_calls_payload(tool_calls):
    """
    converts our collected tool calls into the dictionary format that 
    that the API expects inside assistant message 
    """

    payload=[]
    for tool_call in tool_calls:
        tool_call_dict={
            "id":tool_call.id,
            "type":"function",
            "function":{
                "name":tool_call.function.name,
                "arguments":tool_call.function.arguments 
            }
        }
        payload.append(tool_call_dict)
    return payload


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
        full_response,tool_calls = stream_chat(messages)

        if not tool_calls:
            if full_response:
                messages.append({
                    "role": "assistant",
                    "content": full_response
                })
            break

        log(f"step {step+1}: model requested {len(tool_calls)} tools")

        messages.append({
            "role":"assistant",
            "content":full_response,
            "tool_calls":build_tool_calls_payload(tool_calls)
        })
        #for loop for all tools required by LLM 
        for tool_call in tool_calls:
            result =run_tool(tool_call)
           # appending tool response to messages 
            messages.append(
                {
                    "role":"tool",
                    "tool_call_id":tool_call.id,
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

