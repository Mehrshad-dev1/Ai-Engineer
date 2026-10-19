# agent.py — THE AGENT LOOP
import json
from config import CLIENT, MODEL, MAX_STEPS
from registry import TOOLS, TOOL_FNS
from safety import approve


def run_turn(context: list) -> str:
    for step in range(MAX_STEPS):
        print(f"→ Asking the model... step:{step+1}/{MAX_STEPS}")
        result = CLIENT.responses.create(model=MODEL, input=context, tools=TOOLS)

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
                context.append({
                    "type": "function_call",
                    "name": item.name,
                    "arguments": item.arguments,
                    "call_id": item.call_id,
                })
        
        #if not any functools break
        if not any(item.type == "function_call" for item in result.output):
            return result.output_text

        for item in result.output:
            if item.type == "function_call":
                args = json.loads(item.arguments)

                #Permitted or unauthorized operations
                if not approve(item.name, args):
                    context.append({
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": "User denied this action.",
                    })
                    continue

                tool_result = TOOL_FNS[item.name](args)
                context.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": str(tool_result),
                })

    return "Stopped: hit the step limit."