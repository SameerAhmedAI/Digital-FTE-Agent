"""Streamlit UI for the social content agent."""

from __future__ import annotations

import textwrap

import streamlit as st

from src.agent import SocialContentAgent


REPO_URL = "https://github.com/SameerAhmedAI/Digital-FTE-Agent"
EXAMPLE_TEXT = "Example: We launched an AI assistant that turns meeting notes into social posts for small teams."


st.set_page_config(page_title="Digital FTE Agent", page_icon="✍️", layout="centered")

st.title("Digital FTE Agent")
st.markdown(
    "<p style='color:#94A3B8; margin-top:-0.5rem;'>"
    "Analyze an announcement, pick the right social strategy, and generate a ready-to-post draft."
    "</p>",
    unsafe_allow_html=True,
)

with st.container(border=True):
    st.caption("Topic or announcement")
    topic = st.text_area(
        "Topic or announcement",
        label_visibility="collapsed",
        placeholder=EXAMPLE_TEXT,
        height=150,
    )
    generate_clicked = st.button("Generate Post", type="primary", use_container_width=True)

if generate_clicked:
    try:
        agent = SocialContentAgent()

        with st.spinner("Analyzing input..."):
            validated_text = agent.take_input(topic)
            analysis = agent.analyze(validated_text)

        with st.spinner("Generating post..."):
            post = agent.generate(validated_text, analysis["platform"], analysis["tone"])

        result = {
            "input": validated_text,
            "analysis": analysis,
            "post": post,
        }

        st.subheader("Detected Strategy")
        platform_column, tone_column = st.columns(2)
        platform_column.metric("Platform", result["analysis"]["platform"])
        tone_column.metric("Tone", result["analysis"]["tone"].title())

        st.subheader("Generated Post")
        wrapped_post = "\n\n".join(
            textwrap.fill(paragraph, width=75)
            for paragraph in result["post"].split("\n\n")
        )
        with st.container(border=True):
            st.code(wrapped_post, language=None)
    except Exception as exc:
        st.error(f"Could not generate post: {exc}")

st.divider()
st.caption(
    "Built with the Gemini API — "
    f"[see GitHub repo for architecture details]({REPO_URL})."
)
