import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("AVALAI_API_KEY"),
    base_url="https://api.avalai.ir/v1",
)
MODEL = "gpt-6-luna"
MAX_STEPS = 4

TOOLS = [
    {
        "type": "function",
        "name": "calculate",
        "description": "Do exact arithmetic on two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["operation", "a", "b"],
        },
    }
]

# static mock vs dynamic mock 
'''
MOCK_RESULTS = {"calculate": "20"}
'''
def mock_calculate(args):
    op, a, b = args["operation"], args["a"], args["b"]
    if op == "add":
        return str(a + b)
    if op == "multiply":
        return str(a * b)
    if op == "subtract":
        return str(a - b)
    if op == "divide":
        return "Error: division by zero" if b == 0 else a / b
    return "0"  

def run_turn(task, max_steps=MAX_STEPS):
    CONTEXT = [{"role": "user", "content": task}]
    order = [] #save the calling order (what and which argumans called)
    for _ in range(max_steps):
        result = client.responses.create(model=MODEL, input=CONTEXT, tools=TOOLS) 
        
        # for monitoring
        for item in result.output:
            if item.type == "function_call":
                print(f"  → model requested: {item.name}({item.arguments})")
            elif item.type == "message":
                print(f"  → model answered (text): {result.output_text!r}")
            else:
                print(f"  → other item type: {item.type}")
                        
        for item in result.output:
            if item.type == "function_call":
                CONTEXT.append({
                    "type": "function_call",
                    "name": item.name,
                    "arguments": item.arguments,
                    "call_id": item.call_id,
                })
        # reach to answer
        if not any(item.type == "function_call" for item in result.output):
            return result.output_text, order

        for item in result.output:                  
            if item.type == "function_call":
                args = json.loads(item.arguments)
                order.append((item.name, args))
                CONTEXT.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": mock_calculate(args),
                })

    return "", order


def judge(task, answer):
    # A separate call to the model: Ask how well this answer performed the task.
    r = client.responses.create(
        model=MODEL,
        instructions="Score 1-10 how well the answer completes the task. Reply with only the number.",
        input=f"Task: {task}\nAnswer: {answer}",
    )
    return r.output_text.strip()


task = "Add 12 and 8, then multiply the result by 5."
answer, order = run_turn(task)

print("tool call order:", order)
print("final answer:", answer)
print("judge score:", judge(task, answer))

# in this example should call 2 times. check manually called it or not
names = [name for name, _ in order]
correct_order = names == ["calculate", "calculate"] and len(order) == 2
print("two calls made in sequence:", correct_order)