from datetime import datetime
import requests
from Utilities.utilities import log
import json
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H %M %S")

def get_city_weather(city):
    url=f"https://wttr.in/{city}?format=3"
    response=requests.get(url,timeout=10)
    response.raise_for_status() # this will raise an http error in case of error 
    return response.text

def user_city():
    return "Delhi"

# tool for web search
TOOLS=[
    {
        "type":"function",
        "function" : {
            "name": "get_current_time",
            "description":"gives the current time on user machine as a formated string"
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_city_weather",
            "description":"gives the current weather for a given city ",
            "parameters":{
                "type":"object",
                "properties":{
                    "city":{
                        "type": "string",
                        "description":"city to get the weather for"
                    }
                },       
                "required":["city"]
                
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"user_city",
            "description":"Tell where the user lives , use when prompt uses phrases like 'my city', 'hometown', 'where i live'",
        }
    }
]
FUNCTION_NAME_TO_FUNCTION_MAP={
    "get_current_time":get_current_time,
    "get_city_weather":get_city_weather ,
    "user_city":user_city
}

def run_tool(tool_call):
    func_name=tool_call.function.name
    func_args={}
    try:
        func_args=json.loads(tool_call.function.arguments or "{}")      #from json string to dict
        log(f"function name{func_name} with {func_args}")
        fn=FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
        result=fn(**func_args)    # dictionary unpacking : converting map to arg , FOR EXAMPLE : fn({"city":"tokyo"}) -----> fn(city="tokyo")
    except Exception as e :
        result=f"Error ${e} in ${func_name}"
    log(f"    >{result}")
    return str(result)
                