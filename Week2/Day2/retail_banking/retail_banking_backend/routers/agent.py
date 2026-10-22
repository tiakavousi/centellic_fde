from agent import ask_with_tools
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/agent", tags=["agent"])

class AgentQuestion(BaseModel):
    question:str = Field(min_length=3)


class ToolUseResponse(BaseModel):
    answer: str
    complete: bool
    tool_calls_made: int
    input_tokens: int
    output_tokens: int
    stop_reason: str


@router.post("/ask")
def ask_agent_with_tools(query: AgentQuestion):
    return ask_with_tools(query.question)