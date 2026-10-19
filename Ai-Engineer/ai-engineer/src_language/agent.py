# agent.py — THE AGENT LOOP
import json
from config import CLIENT, MODEL, MAX_STEPS
from registry import TOOLS, TOOL_FNS


DEBUG = False
MAX_TOOL_OUTPUT_CHARS = 4000


def execute_tool(item) -> str:
    ''' it executes a tool call. It never throws an exception; instead, it returns the error to the model.'''
    try:
        args = json.loads(item.arguments)
    except json.JSONDecodeError:
        return "Error: invalid JSON arguments."

    fn = TOOL_FNS.get(item.name)
    if fn is None:
        return f"Error: unknown tool '{item.name}'."

    try:
        return str(fn(args))[:MAX_TOOL_OUTPUT_CHARS]
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"
    


def run_turn(context:list, calls_log:list|None =None) -> str:
    for step in range(MAX_STEPS):
        print(f"→ Asking the model... step:{step+1}/{MAX_STEPS}")
        result = CLIENT.responses.create(model=MODEL, input=context, tools=TOOLS)

        # -- Monitoring & Debug --
        for item in result.output:
            if item.type == "function_call":
                print(f"  → model requested: {item.name}({item.arguments})")
            elif item.type == "message":
                print(f"  → model answered: {result.output_text!r}")
            else:
                print(f"  → other item type: {item.type}")
        
        if DEBUG:
            u = result.usage
            print(f"[step {step + 1}] in={u.input_tokens} out={u.output_tokens} "
                  f"reasoning={u.output_tokens_details.reasoning_tokens} "
                  f"cost={getattr(result, 'estimated_cost', None)}")


        calls = [i for i in result.output if i.type == "function_call"]
        
        if not calls:
            return result.output_text #final result

        for call in calls:
            if calls_log is not None:
                calls_log.append(call.name)
                
            if DEBUG:
                print(f"  → {call.name}({call.arguments})")
                
            context.append({
                "type": "function_call",
                "name": call.name,
                "arguments": call.arguments,
                "call_id": call.call_id,
            })
            context.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": execute_tool(call),
            })

    return "Stopped: hit the step limit."