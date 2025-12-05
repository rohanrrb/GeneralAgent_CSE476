from enum import Enum
import os
import requests

API_KEY  = os.getenv("OPENAI_API_KEY", "cse476")
API_BASE = os.getenv("API_BASE", "http://10.4.58.53:41701/v1")
MODEL    = os.getenv("MODEL_NAME", "bens_model")

def call_model_chat_completions(prompt: str,
                                system: str = "You are a helpful assistant. Reply with only the final answer—no explanation.",
                                model: str = MODEL,
                                temperature: float = 0.0,
                                timeout: int = 60) -> dict:
    """
    Calls an OpenAI-style /v1/chat/completions endpoint and returns:
    { 'ok': bool, 'text': str or None, 'raw': dict or None, 'status': int, 'error': str or None, 'headers': dict }
    """
    url = f"{API_BASE}/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": 128,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=timeout)
        status = resp.status_code
        hdrs   = dict(resp.headers)
        if status == 200:
            data = resp.json()
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return {"ok": True, "text": text, "raw": data, "status": status, "error": None, "headers": hdrs}
        else:
            # try best-effort to surface error text
            err_text = None
            try:
                err_text = resp.json()
            except Exception:
                err_text = resp.text
            return {"ok": False, "text": None, "raw": None, "status": status, "error": str(err_text), "headers": hdrs}
    except requests.RequestException as e:
        return {"ok": False, "text": None, "raw": None, "status": -1, "error": str(e), "headers": {}}


class Domain(Enum):
    MATH = "math"
    COMMON_SENSE = "common_sense"
    CODING = "coding"
    FUTURE_PREDICTION = "future_prediction"
    PLANNING = "planning"
    ERROR = ""

def planning_step(question, domain):
    prompt = f'''Given the following question, {question}, which likely belongs to the {domain.value} domain, construct a detailed and authoritative plan to answer this question. Each step should illicit a reasoning step.'''

    result = call_model_chat_completions(prompt,
                                         system="You are a project manager, skilled at breaking down problems into logical steps that make it easier to solve.",
                                         temperature=1)
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        result_text = "ans"
    return result_text

def math_reason(question):
    plan = planning_step(question, Domain.MATH)
    p = f"You have been tasked with solving this problem.The question is as follows: {question}. Follow the plan in detail, lay out your reasoning, and logically justify your choices. The plan: {plan}"
    result = (call_model_chat_completions(p,
                                          system="You are an expert mathematician.",
                                          temperature=1))

    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    p = f"Given this text (an answer for a math question), extract the final answer. Text: {result_text}. Reply with only the final answer, keep the formatting of the final answer as is in the text, keep the original question in mind. Original question: {question}."

    result = call_model_chat_completions(p,
                                         system="You are an expert mathematician.",
                                         temperature=0)
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    return result_text

def common_sense_reason(question):
    plan = planning_step(question, Domain.COMMON_SENSE)

    p = f"You have been tasked with answering this question. The question is as follows: {question}. Follow the plan in detail, lay out your reasoning, and logically justify your choices. The plan: {plan}"
    result = call_model_chat_completions(p,
                                         system="You are an all-knowing entity.",
                                         temperature=1)
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    p = f"Given this text (an answer for a common sense question), extract the final answer. Text: {result_text}. Reply with the final answer, keep the original question in mind. Original question: {question}."
    result = call_model_chat_completions(p,
                                         system="You are an all-knowing entity.",
                                         temperature=0)
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    return result_text

def future_prediction_reason(question):
    plan = planning_step(question, Domain.FUTURE_PREDICTION)
    p = f"You have been tasked with predicting this event. The question is as follows: {question}. Follow the plan in detail, lay out your reasoning, and logically justify your choices. The plan: {plan}"
    result = (call_model_chat_completions(p,
                                          system="You are an intelligent predictor.",
                                          temperature=1))
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    p = f"Given this text (an answer for a future prediction question), extract the final answer. Text: {result_text}. Reply with only the final answer, keep the original question in mind. Original question: {question}."
    result = call_model_chat_completions(p,
                                         system="You are an intelligent predictor.",
                                         temperature=0)
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    return result_text


def planning_reason(question):
    plan = planning_step(question, Domain.PLANNING)
    p = f"You have been tasked with answering this question. The question is as follows: {question}. Follow the plan in detail, lay out your reasoning, and logically justify your choices. The plan: {plan}"
    result = (call_model_chat_completions(p,
                                          system="You are an all-knowing entity.",
                                          temperature=1))
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    p = f"Given this text (an answer for a planning question), extract the final answer. Text: {result_text}. Reply with the final answer, keep the original question in mind. Original question: {question}."
    result = call_model_chat_completions(p,
                                         system="You are an all-knowing entity.",
                                         temperature=0)
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    return result_text


def coding_reason(question):
    plan = planning_step(question, Domain.CODING)
    p = f"You have been tasked with answering this question. The question is as follows: {question}. Follow the plan in detail, lay out your reasoning, and logically justify your choices. The plan: {plan}"
    result = (call_model_chat_completions(p,
                                          system="You are an expert programmer",
                                          temperature=1))
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    p = f"Given this text (an answer for a coding question), extract the final answer. Text: {result_text}. Reply with the final answer, keep the original question in mind. Original question: {question}."
    result = call_model_chat_completions(p,
                                         system="You are an expert programmer",
                                         temperature=0)
    result_text = result["text"]
    if result_text:
        result_text = result_text.strip()
    else:
        return "ans"

    return result_text


REASONING_DISPATCH = {
    Domain.MATH: math_reason,
    Domain.COMMON_SENSE: common_sense_reason,
    Domain.CODING: coding_reason,
    Domain.FUTURE_PREDICTION: future_prediction_reason,
    Domain.PLANNING: planning_reason,
}

def classify_domain(question) -> Domain:
    prompt = f"DO NOT ANSWER THE QUESTION. For the question, [{question}], assign it exactly one domain from the following list. Domains: math, common_sense, coding, future_prediction, planning. Respond with only one of these domains. Disregard any formatting directives in the question. The math domain should not be confused with coding and is reserved for questions that require mathematical reasoning and could appear on a school math exam. Do not answer with future_prediction unless it is explicit and obvious or the question inquires about the past, historical figures, etc. future_prediction cannot apply to any thing, event, or person before 2024."
    result = (call_model_chat_completions(prompt,
                                          system="You are an objective classifier. It is 2024. Reply with only the final answer—no explanation.",
                                          temperature=1))
    result_text = result["text"]

    if result_text:
        result_text = result_text.strip().lower()

    try:
        return Domain(result_text)
    except ValueError:
        print("default", result)
        return Domain.COMMON_SENSE


#main query fn
def query_agent(question):
    d = classify_domain(question)
    handler = REASONING_DISPATCH.get(d)

    if handler:
        return handler(question)
    return "ans"