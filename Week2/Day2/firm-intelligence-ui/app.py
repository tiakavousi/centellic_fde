import os
import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")


def _safe_detail(resp):
    try:
        j = resp.json()
        return j.get("detail", str(j)) if isinstance(j, dict) else str(j)
    except ValueError:
        return resp.text[:300]

st.set_page_config(page_title="Firm Intelligence", layout="wide")
st.title("Firm Intelligence")
st.caption(f"API: {API_BASE}")

tab_ask, tab_search, tab_stream = st.tabs(["Ask", "Search", "Firm summary (stream)"])


# --- Feature 1: Ask ---------------------------------------------------------
with tab_ask:
    st.subheader("Ask the agent")
    question = st.text_area("Question", key="ask_q", placeholder="Ask anything about firms, people, or the knowledge base.")
    if st.button("Ask", key="ask_btn"):
        if not question.strip():
            st.warning("Type a question first.")
        else:
            try:
                r = requests.post(
                    f"{API_BASE}/agent/ask",
                    json={"question": question},
                    timeout=120,
                )
            except requests.RequestException as e:
                st.error(f"Request failed: {e}")
            else:
                if r.status_code == 200:
                    data = r.json()
                    if data.get("complete"):
                        st.success("Answer")
                    else:
                        st.warning(
                            f"Agent did not complete (stop_reason={data.get('stop_reason')}). "
                            "Partial answer below."
                        )
                    st.write(data.get("answer") or "_(no answer text)_")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Tool calls", data.get("tool_calls_made", 0))
                    c2.metric("Input tokens", data.get("input_tokens", 0))
                    c3.metric("Output tokens", data.get("output_tokens", 0))
                else:
                    detail = _safe_detail(r)
                    st.error(f"API error {r.status_code}: {detail}")


# --- Feature 2: Search only -------------------------------------------------
with tab_search:
    st.subheader("Knowledge search")
    q = st.text_input("Query", key="search_q")
    top_k = st.slider("top_k", 1, 7, 3, key="search_k")
    if st.button("Search", key="search_btn"):
        if not q.strip():
            st.warning("Type a query first.")
        else:
            try:
                r = requests.post(
                    f"{API_BASE}/knowledge/search",
                    json={"question": q, "top_k": top_k},
                    timeout=60,
                )
            except requests.RequestException as e:
                st.error(f"Request failed: {e}")
            else:
                if r.status_code == 200:
                    hits = r.json()
                    if not hits:
                        st.info("No results.")
                    else:
                        for h in hits:
                            st.markdown(
                                f"**{h.get('title', h.get('id', '?'))}** — score `{h.get('score'):.3f}`"
                            )
                elif r.status_code == 409:
                    st.warning(
                        "Index has not been built yet. "
                        f"POST {API_BASE}/knowledge/index to build it. "
                        f"(server said: {_safe_detail(r)})"
                    )
                else:
                    st.error(f"Search failed ({r.status_code}): {_safe_detail(r)}")


# --- Feature 3: Streaming firm summary --------------------------------------
with tab_stream:
    st.subheader("Firm summary (streamed)")
    firm_id = st.number_input("Firm id", min_value=1, step=1, value=1, key="firm_id")
    if st.button("Summarise", key="stream_btn"):
        placeholder = st.empty()
        buf = []
        try:
            with requests.get(
                f"{API_BASE}/firms/{int(firm_id)}/summary/stream",
                stream=True,
                timeout=(10, 300),
            ) as r:
                if r.status_code != 200:
                    st.error(f"API error {r.status_code}: {_safe_detail(r)}")
                else:
                    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                        if not chunk:
                            continue
                        buf.append(chunk if isinstance(chunk, str) else chunk.decode("utf-8", "replace"))
                        placeholder.markdown("".join(buf))
                    if not buf:
                        st.info("Stream ended with no content.")
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")
