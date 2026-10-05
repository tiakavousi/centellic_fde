from typing import Any
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from routers.complaints import get_complaint_or_404
from llm import generate, stream
from prompts.prompts import build_complaint_summary_user_prompt, SYSTEM_PROMPT
from llm import generate_structured
from schemas.complaints import ComplaintAnalysis, ComplaintAnalyzeResponse

router = APIRouter(prefix="/llm", tags=["llm", "complaints"])

@router.post("/complaints/{complaint_id}/summary")
def generate_complaint_summary(complaint_id:int) -> dict[str, Any]:
    complaint = get_complaint_or_404(complaint_id)
    complaint_summary = generate(SYSTEM_PROMPT, build_complaint_summary_user_prompt(complaint))
    return {
        "id": complaint["id"],
        "customer_id": complaint["customer_id"],
        "product": complaint["product"],
        "severity": complaint["severity"],
        **complaint_summary
    }

@router.get("/complaints/summary/{complaint_id}/stream")
def generate_complaint_summary_stream(complaint_id: int) :
    complaint = get_complaint_or_404(complaint_id)
    chunks = stream(SYSTEM_PROMPT,build_complaint_summary_user_prompt(complaint))
    return StreamingResponse(chunks,media_type="text/plain")

@router.post("/complaints/analyse/{complaint_id}")
def analyse_complaint(complaint_id:int) -> ComplaintAnalyzeResponse:
    complaint = get_complaint_or_404(complaint_id)
    structured_result =  generate_structured(
        SYSTEM_PROMPT,
        build_complaint_summary_user_prompt(complaint),
        response_model=ComplaintAnalysis
    )
    return {
        "id": complaint["id"],
        "customer_id": complaint["customer_id"],
        "analysis": structured_result["structured_output"],
        "input_tokens": structured_result["input_tokens"],
        "output_tokens": structured_result["output_tokens"],
        "stop_reason": structured_result["stop_reason"]
    } 
    

