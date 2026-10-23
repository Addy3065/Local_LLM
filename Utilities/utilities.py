import os 
start_log="\033[90m"
end_log="\033[0m"
def log(text):
    if os.getenv("DEBUG")=="True":
        print(f"  {start_log}{text}{end_log}")          
    