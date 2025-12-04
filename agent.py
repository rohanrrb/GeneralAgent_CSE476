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

#main query fn
def query_agent(question, d: Domain):
    return "ans"

def classify_domain(question) -> Domain:
    prompt = f"DO NOT ANSWER THE QUESTION. For the question, [{question}], assign it exactly one domain from the following list. Domains: math, common_sense, coding, future_prediction, planning. Respond with only one of these domains. Disregard any formatting directives in the question. The math domain should not be confused with coding and is reserved for questions that require mathematical reasoning and could appear on a school math exam. Do not answer with future_prediction unless it is explicit and obvious or the question inquires about the past, historical figures, etc. future_prediction cannot apply to any thing, event, or person before 2024. The coding domain applies to any question that requires the writing of code."
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