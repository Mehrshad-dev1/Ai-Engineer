# judge.py: judge model for DeepEval
import json
import re
import tempfile
import pathlib

from config import CLIENT, MODEL
import language_tool
from agent import run_turn
from main import SYSTEM_PROMPT 

from deepeval.models import DeepEvalBaseLLM
from deepeval.metrics import AnswerRelevancyMetric, GEval, ToolCorrectnessMetric
from deepeval.test_case import LLMTestCase, LLMTestCaseParams, SingleTurnParams, ToolCall


# --LLM as Judge
class Judge(DeepEvalBaseLLM):
    """sumary_line
    DeepEvalBaseLLM is a abstract-class. 
    This means it declares several methods that any subclass must implement:
    load_model:call model , generate , a_generate , get_model_name
    """
     
    def __init__(self, model_name:str=MODEL, client=CLIENT):
        self.model_name = model_name
        self.client = client

    def load_model(self):
        return CLIENT

    def generate(self, prompt:str, schema=None):
        '''
        sometimes, DeepEval requires not just text from the judge( depends on the model), 
        but a response in a specific format. It defines that format using a class 
        (specifically a Pydantic model) and passes it to the `generate` method. For example:
        class ScoreReason(BaseModel):
            score: int
            reason: str
        '''
        if schema is not None:
            prompt += "\n\nReply with a single valid JSON object only. No markdown, no extra text."
        r = self.client.responses.create(model=self.model_name, input=prompt)
        text = r.output_text.strip()

        if schema is None:
            return text

        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
        return schema(**json.loads(text))


    async def a_generate(self, prompt: str, schema=None):
        return self.generate(prompt, schema)
    
    
    def get_model_name(self) -> str:
        return self.model_name


def run_assistant(prompt:str, seed_words:list|None=None):
    '''
    Each test has its own temporary vocabulary notebook so 
    that the actual `vocab.json` does not get polluted.
    '''
    
    vocab = pathlib.Path(tempfile.mkdtemp()) / "vocab.json"
    if seed_words:
        vocab.write_text(json.dumps(seed_words, ensure_ascii=False), encoding="utf-8")
    language_tool.VOCAB_FILE = vocab

    calls: list[str] = []
    context = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    answer = run_turn(context, calls_log=calls)
    return answer, calls


CASES = [
    {"id": "save", "prompt": "Please save the word 'apple' (سیب) in my vocabulary.",
     "expected_tools": ["save_word"]},
    {"id": "quiz", "prompt": "Quiz me on my saved words.",
     "expected_tools": ["get_quiz_words"],
     "seed": [{"word": "apple", "meaning": "سیب", "example": ""},
              {"word": "book", "meaning": "کتاب", "example": ""}]},
    {"id": "correct", "prompt": "Correct my sentence: 'She go to school yesterday.'",
     "expected_tools": []},
    {"id": "chat", "prompt": "Hi! How are you today?",
     "expected_tools": []},
]

judge = Judge()

# -- metrics that need Judge-LLM:
clarity = GEval(
    name="Beginner Clarity",
    criteria=("Is the output simple enough for an A2 English learner? "
              "Persian translations are allowed and expected; judge only the English part."),
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    model=judge, threshold=0.75, async_mode=False,
)

correction = GEval(
    name="Correction Quality",
    evaluation_steps=[
        "Check that the output fixes the grammar error in the learner's sentence.",
        "Check that the output briefly explains the mistake (Persian is fine).",
        "Penalize long or complicated explanations.",
    ],
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    model=judge, threshold=0.75, async_mode=False,
)

relevancy = AnswerRelevancyMetric(threshold=0.75, model=judge, async_mode=False)


#report the results together
def report(metric, tc):
    '''metric , cases'''
    metric.measure(tc)
    status = "PASS" if metric.is_successful() else "FAIL"
    print(f" [{status}] {metric.__class__.__name__:<22} score={metric.score:.2f}")
    if not metric.is_successful():
        print(f"reason: {metric.reason}")



for case in CASES:
    answer, calls = run_assistant(case["prompt"], case.get("seed"))
    print(f"\n== {case['id']} ==")
    print(f"   tools called: {calls}")
    print(f"   answer: {answer[:150]!r}")

    tc = LLMTestCase(
        input=case["prompt"],
        actual_output=answer,
        tools_called=[ToolCall(name=n) for n in calls],
        expected_tools=[ToolCall(name=n) for n in case["expected_tools"]],
    )

    #without judge
    if case["expected_tools"]:
        report(ToolCorrectnessMetric(threshold=0.5, model=judge), tc)
    else:
        ok = calls == []
        print(f"   [{'PASS' if ok else 'FAIL'}] no-tool check (plain assert)")

    #with judge
    report(relevancy, tc)
    report(clarity, tc)
    if case["id"] == "correct":
        report(correction, tc)








#metrics
clarity = GEval(
    name="Beginner Clarity",
    criteria="Is the actual output simple and clear enough for an A2-level English learner?" 
            "Persian translations are allowed and expected; judge only the English part",
    evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT],
    model=judge,
    threshold=0.75,
    async_mode=False,
)

good = LLMTestCase(
    input="What does 'table' mean?",
    actual_output="'Table' means میز. Example: I put my book on the table.",
)
bad = LLMTestCase(
    input="What does 'table' mean?",
    actual_output="Table denotes a polysemous lexeme referring to a horizontal furniture "
                  "artifact or a tabular data arrangement.",
)

for name, case in [("good", good), ("bad", bad)]:
    clarity.measure(case)
    print(f"{clarity} \n")
    print(f"{name}: score={clarity.score:.2f} passed={clarity.is_successful()}")
    print(f"  reason: {clarity.reason}\n")