import json

import agent_tools
import config  # noqa: F401 — loads .env.local
import knowledge
from agent_tools import SEARCH_TOOLS
from llm import generate_with_tools
from prompts.prompts import AGENT_SYSTEM_PROMPT

MAX_ITERATIONS = 4

def ask_with_tools(question: str) -> dict:
    """Run the tool-use loop until the model answers, or the limit is hit."""

    messages = [{"role": "user", "content": question}]
    total_input_tokens = 0
    total_output_tokens = 0
    tool_calls_made = 0
    last_stop_reason = None

    for _ in range(MAX_ITERATIONS):
        response = generate_with_tools(
            system=AGENT_SYSTEM_PROMPT,
            messages=messages,
            tools=SEARCH_TOOLS,
        )
        last_stop_reason = response.stop_reason
        total_input_tokens += response.usage.input_tokens
        total_output_tokens += response.usage.output_tokens

        if response.stop_reason != "tool_use":
            final_text = next(
                (b.text for b in response.content if b.type == "text"), ""
            )
            return {
                "answer": final_text,
                "complete": True,
                "tool_calls_made": tool_calls_made,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "stop_reason": response.stop_reason,
            }

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result_text, is_error = _execute_tool(block.name, block.input)
            if not is_error:
                tool_calls_made += 1
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result_text,
                "is_error": is_error,
            })

        messages.append({"role": "user", "content": tool_results})

    return {
        "answer": "Could not reach a final answer within the iteration limit.",
        "complete": False,
        "tool_calls_made": tool_calls_made,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "stop_reason": last_stop_reason,
    }


def _execute_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    """Run the requested tool. Returns (result_text, is_error)."""
    if name == "search_knowledge_base":
        if "query" not in tool_input:
            return 'Error: missing required field "query"', True
        try:
            results = knowledge.search(tool_input["query"], top_k=3)
        except RuntimeError as e:
            return f"Error: {e}", True
        if not results:
            return "No relevant documents found", False
        formatted = "\n\n".join(
            f"[{r['id']}] {r['title']} (score {r['score']:.2f})\n{r['text']}"
            for r in results
        )
        return formatted, False

    if name == "check_sla_status":
        cid = tool_input.get("complaint_id")
        if cid is None:
            return 'Error: missing "complaint_id"', True
        result = agent_tools.check_sla_status(cid)
        return json.dumps(result, default=str), False

    return f"Unknown tool: {name}", True
