# registry.py — the bridge between "what the model see" & "is real the function run"

from language_tool import save_word , list_words , get_quiz_words 


# -- Tools schema -- 
TOOLS = [
    {"type":'function' ,
      "name":'save_word' ,
      "description":'save a new English vocabulary word the learner wants to remember.' ,
      "parameters": {"type":'object' ,
                     "properties": {"word": {"type": 'string'} ,
                                    "meaning": {"type":'string', "description":'Persian meaning'} ,
                                    "example": {"type":'string'} },
                    "required":["word", "meaning"]  }  } ,
    
    {"type": 'function', 
    "name": 'save_word',
    "description": 'save a new english vocabulary word the learner wants to remember.',
    "parameters": {"type": 'object',
                   "properties": {"word": {"type": 'string'},
                               "meaning": {"type": 'string', "description": 'Persian meaning'},
                               "example": {"type": 'string'}},
                    "required": ['word', 'meaning'] } },
                    
    {"type": "function", 
    "name": "list_words",
    "description": "show all vocabulary words the learner has saved.",
    "parameters": {"type": "object", 
                    "properties": {}, 
                    "required": [] }  },
                    
    {"type": "function", 
    "name": "get_quiz_words",
    "description": "get random saved words to quiz the learner.",
    "parameters": {"type": "object",
                    "properties": {"n": {"type": "integer"}}, 
                    "required": []}}
]


# -- TOOL_FNS dispatch 
TOOL_FNS = {
    "save_word": lambda x: save_word(x["word"], x["meaning"], x.get("example", "")),
    "list_words": lambda x: list_words(),
    "get_quiz_words": lambda x: get_quiz_words(x.get("n", 3)),
}