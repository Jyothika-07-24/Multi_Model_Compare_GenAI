import streamlit as st
from main import ask, MODELS, PRICES

st.set_page_config(page_title="Multi-Model Comparison Tool", layout="wide")

st.title("Multi-Model Comparison Tool")
st.caption("Send one question to multiple LLMs via OpenRouter and compare their answers, speed, and cost side by side.")

if "running" not in st.session_state:
    st.session_state.running = False

question = st.text_area(
    "Your question",
    placeholder="e.g. What is the difference between machine learning and deep learning?",
    height=120,
)

selected_models = st.multiselect(
    "Models to query",
    options=MODELS,
    default=MODELS,
)

run = st.button(
    "Compare models",
    type="primary",
    disabled=st.session_state.running or not question or not selected_models,
)

st.caption("Prices are illustrative estimates — verify current rates at openrouter.ai/models.")

if not question:
    st.warning("Enter a question above to get started.")
elif run:
    st.session_state.running = True
    results = []

    with st.spinner("Querying models…"):
        for model in selected_models:
            try:
                answer, latency, in_tokens, out_tokens, cost = ask(question, model)
                results.append({
                    "model":   model,
                    "answer":  answer,
                    "latency": latency,
                    "cost":    cost,
                    "error":   None,
                })
            except Exception as e:
                results.append({
                    "model":   model,
                    "answer":  None,
                    "latency": None,
                    "cost":    None,
                    "error":   str(e),
                })

    st.session_state.running = False

    cols = st.columns(len(results))
    for col, r in zip(cols, results):
        with col:
            st.subheader(r["model"])
            if r["error"]:
                st.error(r["error"])
            else:
                m1, m2 = st.columns(2)
                m1.metric("Latency", f"{r['latency']:.2f} s")
                m2.metric("Cost", f"${r['cost']:.6f}")
                st.write(r["answer"])
