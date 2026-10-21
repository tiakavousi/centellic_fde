"""The /knowledge/ask flow as a LangGraph graph.

    START -> retrieve -> gate -+-> answer -> check -> END
                               |
                               +-> refuse --------> END      (nothing relevant: no model call)

Each node does one job and returns only what it changes. The gate becomes a conditional edge:
the graph itself decides whether the model is ever called.
"""

from typing import TypingDict

import context
import gate
import grounding
import knowledge_store
import lc_model
import llm
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph import END, START, StateGraph


REFUSAL_REASON = "No document in the corpus is relevant to that question"

class AskState(TypingDict, total=False):
    question: str
    top_k: int
    cosine_floor: float
    rerank_floor: float
    hits: list[dict]
    usable: list[dict]
    answer: str
    input_tokens: int
    output_tokens: int
    stop_reason: str
    result: dict

def retrieve(state: AskState) -> dict:
    return {"hits": knowledge_store.search(state["question"], state["top_k"])}

def apply_gate(state: AskState) -> dict:
    usable = [hit for hit in state["hits"]
            if gate.is_usable(hit, state["cosine_floor"], state["rerank_floor"])
        ]
    return {"usable": usable}

# this one is different ... it isn't a node
# it does not change the form ... it return the name of the next node
# LangGraph calls it straight after the gate, and follows the path it names

def after_gate(state: AskState) -> str:
    """
    Our conditional edge... answer if anything passed the gate, otherwise refuse
    """
    return "answer" if state["usable"] else "refuse"
