from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.models import GPTModel
from tqdm import tqdm
import json

# Create a custom OpenAI model
custom_model = GPTModel(model="gpt-4o", temperature=0.0)

# Define metric configurations
metric_configs = [
    {
        "name": "Explainability and Reasoning",
        "criteria": (
            "Evaluate whether the report clearly and transparently explains not only the final conclusion, but also the reasoning process and supporting evidence in a step-by-step, understandable manner. "
            "The explanation should guide the reader through the logic in a way that supports comprehension, allowing the reader to see how and why each inference was made. "
            "Assess whether the structure of the reasoning helps build an intuitive understanding of the issue, making the conclusion feel not only justified but inevitable. "
            "The report should avoid unexplained jumps in logic and instead provide a smooth progression that educates the reader along the way, enhancing trust and clarity."
        )
    },
    {
        "name": "Justification with Evidence",
        "criteria": (
            "Determine whether the statements and claims made in the report are explicitly justified with relevant, specific, and clearly cited evidence from the source document(s). "
            "This includes direct quotations, clause references, or document identifiers that can be independently verified. "
            "The justification should be traceable, meaning a reader should be able to locate the original source material and see how it supports the statement. "
            "Also consider whether the report references multiple relevant sources where appropriate, to build a more complete and contextually grounded justification rather than relying on a single source. "
        )
    },
    {
        "name": "Contextual and Legal Understanding",
        "criteria": (
            "Evaluate whether the report demonstrates a deep and accurate understanding of the document itself, the legal terminology it uses, and the broader context in which it is situated. "
            "Assess the correctness of interpretations of clauses, definitions, and legal constructs, including any implicit legal norms or common contractual language. "
            "Additionally, evaluate whether the user's query is correctly understood and interpreted in its full scope — including its legal, contextual, and practical dimensions. "
            "This includes identifying the legal issue(s) being raised, any implied assumptions or concerns, and the broader objectives behind the question."
        )
    },
    {
        "name": "Handling Ambiguity",
        "criteria": "Determine if the report identifies and handles ambiguities in the source material appropriately, such as by discussing multiple interpretations or providing reasoning for one over another."
    },
    {
        "name": "Acknowledgment of Knowledge Gaps",
        "criteria": "Evaluate whether the report explicitly acknowledges when there is insufficient information in the source material to draw a conclusion, and avoids speculation."
    },
    {
        "name": "Conciseness and Precision",
        "criteria": "Assess whether the report communicates clearly and efficiently, avoiding unnecessary repetition or verbosity while still conveying key points thoroughly."
    },
    {
        "name": "Coherence and Organization",
        "criteria": "Check if the report is logically structured, easy to follow, and transitions smoothly between sections or ideas."
    },
    {
        "name": "Relevance and Focus",
        "criteria": "Determine whether the report stays on topic and maintains a clear focus on answering the user's query without introducing off-topic content."
    },
    {
        "name": "Completeness",
        "criteria": (
            "Evaluate if the report covers all important aspects of the query and does not omit any key points that may affect the conclusion or understanding. "
            "The report should demonstrate a broad and holistic view of the problem, approaching the solution from multiple relevant angles or perspectives. "
            "It should avoid overly narrow reasoning and instead include a contextually complete analysis."
        )
    }
]

# Create metrics
metrics = [
    GEval(
        name=config["name"],
        criteria=config["criteria"],
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
        model=custom_model
    ) for config in metric_configs
]

# Load data
with open("./results/predictionsPAKTON.json", "r", encoding="utf-8") as f:
    dataPAKTON = json.load(f)

with open("./results/predictionsGPTreasoning.json", "r", encoding="utf-8") as f:
    dataGPT = json.load(f)

# Prepare test cases
test_cases = {"PAKTON": [], "GPT": []}
for index, (pakton_item, gpt_item) in enumerate(zip(dataPAKTON, dataGPT)):
    input_text = pakton_item["system_prompt"]['userQuery'] + '\n' + pakton_item["system_prompt"]['userContext']
    test_cases["PAKTON"].append(LLMTestCase(input=input_text, actual_output=pakton_item["reasoning"], name=f'PAKTON-{index+1}'))
    test_cases["GPT"].append(LLMTestCase(input=input_text, actual_output=gpt_item["reasoning"], name=f'GPT-{index+1}'))

# File to write progressively
output_path = "./results/geval_scores.json"
scores = {}

# Evaluation loop with progress bar
for idx, (pakton_case, gpt_case) in enumerate(tqdm(zip(test_cases["PAKTON"], test_cases["GPT"]), total=len(test_cases["PAKTON"]), desc="Evaluating")):
    case_id = f"test_case_{idx+1}"
    scores[case_id] = {
        "input": pakton_case.input,
        "PAKTON": {"output": pakton_case.actual_output},
        "GPT": {"output": gpt_case.actual_output}
    }

    for model_name, test_case in [("PAKTON", pakton_case), ("GPT", gpt_case)]:
        for metric in metrics:
            metric.measure(test_case)
            scores[case_id][model_name][metric.name] = {
                "score": metric.score,
                "reason": metric.reason
            }

    # Save progress after each test case
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)