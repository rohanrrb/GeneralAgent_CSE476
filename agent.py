from enum import Enum

class Domain(Enum):
    MATH = "math"
    GENERAL = "general"
    COMMON_SENSE = "common_sense"
    CODING = "coding"
    FUTURE_PREDICTION = "future_prediction"
    PLANNING = "planning"

#main query fn
def query_agent(question):
    return "ans"

def classify_domain(question) -> Domain:
    return Domain.MATH