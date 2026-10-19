import json
import os
from dotenv import load_dotenv
from openai import OpenAI


#load .env into os.environ
load_dotenv()
api_key = os.getenv("AVALAI_API_KEY")
if not api_key:
    raise ValueError("AVALAI_API_KEY not found. Check your .env file.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.avalai.ir/v1",
)

#MODEL 
MODEL = "gpt-6-luna"
#CONTEXT
CONTEXT = [{"role": "user", "content": "What is 48291 times 7734?"}]

#FUNCTION
def calculate(operation:str, a:float, b:float) -> float:
    if operation == "add":
        return a + b
    if operation == "subtract":
        return a - b
    if operation == "multiply":
        return a * b
    if operation == "divide":
        return "Error: division by zero" if b == 0 else a / b
    return f"Error: unknown operation {operation}"


# The description the MODEL sees: name, purpose, argument shape.
TOOLS = [
    {
        "type": "function",
        "name": "calculate",
        "description": "Do exact arithmetic on two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                },
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["operation", "a", "b"],
        },
    }
]

#STEP1: ask the model 
print("→ Asking the model...")
first = client.responses.create(model=MODEL, input=CONTEXT, tools=TOOLS)
CONTEXT += [item.model_dump(exclude_none=True) for item in first.output]

# STEP2: call tools
for item in first.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        print(f'----- \n args : \n {args} \n -----')
        print(f"\n ----- \n model asked: \n  {item.name}({args}) \n -----")   
        result = calculate(args["operation"], args["a"], args["b"])
        print(f"\n ----- \n we computed: \n {result} \n -----")
        CONTEXT.append({
            "type": "function_call_output",
            "call_id": item.call_id,   
            "output": str(result),
        })

print(f'****\n CONTEXT: \n {CONTEXT} \n **** \n')

#STEP 3: ask again. Now the model has the number and writes the answer.
print("→ Asking again with the result...")
second = client.responses.create(model=MODEL, input=CONTEXT, tools=TOOLS)
print("\n ----- \n Final answer: \n" , second.output_text)

