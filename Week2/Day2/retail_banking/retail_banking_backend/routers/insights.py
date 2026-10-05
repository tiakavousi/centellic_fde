from typing import Any
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from routers.complaints import get_complaint_or_404
from llm import generate, stream
from prompts.prompts import build_complaint_summary_user_prompt, SYSTEM_PROMPT, build_complaint_analysis_user_prompt
import llm
from schemas.complaints import ComplaintAnalysis, ComplaintAnalyzeResponse
from routers.customers import get_customer_or_404

router = APIRouter(prefix="/llm", tags=["llm", "complaints"])

@router.post("/complaints/{complaint_id}/summary")
def generate_complaint_summary(complaint= Depends(get_complaint_or_404)) -> dict[str, Any]:
    complaint_summary = generate(SYSTEM_PROMPT, build_complaint_summary_user_prompt(complaint))
    return {
        "id": complaint["id"],
        "customer_id": complaint["customer_id"],
        "product": complaint["product"],
        "severity": complaint["severity"],
        **complaint_summary
    }

@router.get("/complaints/{complaint_id}/summary/stream")
def generate_complaint_summary_stream(complaint= Depends(get_complaint_or_404)) -> StreamingResponse:
    chunks = stream(SYSTEM_PROMPT,build_complaint_summary_user_prompt(complaint))
    return StreamingResponse(chunks,media_type="text/plain")

@router.post("/complaints/{complaint_id}/analyse")
def analyse_complaint(complaint= Depends(get_complaint_or_404)) -> ComplaintAnalyzeResponse:
    customer = get_customer_or_404(complaint["customer_id"])
    structured_result =  llm.generate_structured(
        SYSTEM_PROMPT,
        build_complaint_analysis_user_prompt(complaint, customer),
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

@router.get("/complaints/{complaint_id}/summary/estimate")
def estimate(complaint= Depends(get_complaint_or_404)):
    tokens = llm.estimate_input_tokens(SYSTEM_PROMPT, build_complaint_summary_user_prompt(complaint))
    return{
        "id": complaint["id"],
        "estimated_input_tokens": tokens,
        "model": llm.MODEL

    } 
    

