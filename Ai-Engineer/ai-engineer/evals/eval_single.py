import os
import json
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

API_KEY = os.getenv('AVALAI_API_KEY')
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.avalai.ir/v1")

MODEL = "gpt-6-luna"


TOOLS = [
    {
        "type": 'function',
        "name": 'calculate',
        "description": 'Do exact arthemetic on 2 number',
        "parameters":{
            "type":'object',
            "propertise": {
                "operation": {"type": 'string' , "enum":["add", "subtract", "multiply", "divide"]},
                "a": {"type": 'number'},
                "b": {"type": 'number'}},
            "required":  ['operation', 'a', 'b']
        }
        
    }
]


# prompt -> expected tool(s). Empty list=should call NO tool.
CASES = [
    {"prompt": "What is 48291 times 7734?", "expect": ["calculate"]}, #pass
    {"prompt": "What's 100 divided by 4?", "expect": ["calculate"]}, #pass
    {"prompt": "Add 17 and 25 for me", "expect": ["calculate"]}, #pass
    {"prompt": "What is the capital of France?", "expect": []}, #pass
    {"prompt": "Tell me a joke", "expect": []}, #pass
    {"prompt": "subtract 10 and 2 for me", "expect": []} #fail
]


def tools_chosen(prompt):
    result = client.responses.create(model= MODEL, 
                                    input= [{"role": "user", "content": prompt}],
                                    tools= TOOLS,
                                    tool_choice= 'auto')
   
    return [item.name for item in result.output if item.type == "function_call"]


passed = 0
for case in CASES:
    chosen = tools_chosen(case["prompt"])
    ok = set(chosen) == set(case["expect"])
    passed += ok
    print(f"[{'PASS' if ok else 'FAIL'}] {case['prompt']!r} chose={chosen}")

print(f"\n{passed}/{len(CASES)} passed") 