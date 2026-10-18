import json

import agent_tools
import config  # noqa: F401 — loads .env.local
from agent_tools import SEARCH_TOOLS
from llm import generate_with_tools
from prompts.prompts import AGENT_SYSTEM_PROMPT

MAX_ITERATIONS = 4

def ask_with_tools(question: str) -> dict:
    """Run the Claude tool-use loop for a single user question.

    Sends the question with AGENT_SYSTEM_PROMPT and SEARCH_TOOLS. On each turn:
    if the model stops with anything other than 'tool_use', the loop returns
    the final text; otherwise it executes every tool_use block via _execute_tool,
    appends the tool_result blocks back to the conversation, and continues.
    Tool failures (unknown tool, missing args, exceptions inside a tool) are
    reported back to the model as tool_result with is_error=True rather than
    raised, so the model can recover or refuse. Only successful tool executions
    count toward tool_calls_made. If MAX_ITERATIONS is reached without a final
    answer, the loop returns complete=False with a sentinel message.

    Args:
        question: The user's natural-language question.

    Returns:
        {answer, complete, tool_calls_made, input_tokens, output_tokens, stop_reason}.
        input_tokens and output_tokens are summed across every turn in the loop.
    """

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
    if name == "get_complaint":
        cid = tool_input.get("complaint_id")
        if cid is None:
            return 'Error: missing "complaint_id"', True
        result = agent_tools.get_complaint(cid)
        is_error = "error" in result
        return json.dumps(result, default=str), is_error

    if name == "search_knowledge_base":
        if "query" not in tool_input:
            return 'Error: missing required field "query"', True
        results = agent_tools.search_knowledge_base(tool_input["query"], top_k=3)
        if isinstance(results, dict) and "error" in results:
            return f"Error: {results['detail']}", True
        if not results:
            return "No relevant documents found", False
        formatted = "\n\n".join(
            f"[{r['id']}] {r['title']} (score {r['score']:.2f})\n{r['body']}"
            for r in results
        )
        return formatted, False

    if name == "check_sla_status":
        cid = tool_input.get("complaint_id")
        if cid is None:
            return 'Error: missing "complaint_id"', True
        result = agent_tools.check_sla_status(cid)
        return json.dumps(result, default=str), False

    if name == "find_similar_complaints":
        result = agent_tools.find_similar_complaints(
            product=tool_input.get("product"),
            theme=tool_input.get("theme"),
            vulnerable_only=tool_input.get("vulnerable_only", False),
            limit=tool_input.get("limit", agent_tools.DEFAULT_SIMILAR_RESULTS),
        )
        is_error = "error" in result
        return json.dumps(result, default=str), is_error

    return f"Unknown tool: {name}", True
