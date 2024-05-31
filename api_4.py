import os
import streamlit as st

# デバッグ用に環境変数を出力
st.write(f"DEBUG: OPENAI_API_KEY is set to: {os.getenv('OPENAI_API_KEY')}")

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import (
    SystemMessage,
    HumanMessage,
    AIMessage
)
from langchain_community.callbacks.manager import get_openai_callback

def init_page():
    st.set_page_config(
        page_title="My Great ChatGPT",
        page_icon="🤗"
    )
    st.header("My Great ChatGPT 🤗")
    st.sidebar.title("Options")

def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="You are a helpful assistant.")
        ]
        st.session_state.costs = []

def select_model():
    model = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
    if model == "GPT-3.5":
        model_name = "gpt-3.5-turbo"
    else:
        model_name = "gpt-4"

    temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.0, step=0.01)

    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        st.error("OPENAI_API_KEY is not set.")
        return None

    return ChatOpenAI(temperature=temperature, model_name=model_name, openai_api_key=openai_api_key)

def get_answer(llm, messages):
    with get_openai_callback() as cb:
        answer = llm(messages)
    return answer.content, cb.total_cost

def main():
    init_page()

    llm = select_model()
    if not llm:
        return  # APIキーが設定されていない場合は処理を中断

    init_messages()

    if user_input := st.cha
