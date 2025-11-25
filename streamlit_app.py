import os
import streamlit as st
from openai import OpenAI
from typing import List, Dict


def main():
    st.set_page_config(page_title="야식 추천 챗봇", page_icon="🍜")

    st.title("🍽️ 야식 추천 챗봇")
    st.write(
        "사용자의 기호와 상황에 맞춰 야식 메뉴를 추천하고 자연스럽게 대화를 이어가는 챗봇입니다."
    )

    # Read API key from Streamlit secrets or environment variables.
    # This avoids asking the user for the API key in the web UI.
    # Streamlit secrets often stored as OPENAI_API_KEY = "sk-...".
    openai_api_key = (
        st.secrets.get("OPENAI_API_KEY")
        or (st.secrets.get("openai") or {}).get("api_key")
        or os.environ.get("OPENAI_API_KEY")
    )
    if not openai_api_key:
        st.error(
            "OpenAI API 키가 설정되어 있지 않습니다. `.streamlit/secrets.toml`에 `OPENAI_API_KEY = \"sk-...\"` 형태로 추가하거나 환경 변수 `OPENAI_API_KEY`를 설정해주세요."
        )
        st.stop()

    # Create OpenAI client using the official Python SDK
    client = OpenAI(api_key=openai_api_key)

    # Initialize session state for conversation
    if "messages" not in st.session_state:
        # store assistant and user messages as {"role": "user"|"assistant", "content": "..."}
        st.session_state.messages: List[Dict[str, str]] = []

    # Sidebar options
    with st.sidebar:
        st.header("설정")
        # Optionally allow small behavior control
        language = st.selectbox("대화 언어", ["한국어", "한국어(공손형)", "한국어(친근한)"])
        if st.button("대화 초기화", key="reset"):
            st.session_state.messages = []
            st.experimental_rerun()

    # System message to instruct the assistant's behavior
    style = ""
    if language == "한국어(공손형)":
        style = "정중하고 공손한 어투로,"
    elif language == "한국어(친근한)":
        style = "친근하고 가벼운 어투로,"
    else:
        style = "자연스럽고 표준적인 한국어로,"

    system_message = (
        f"당신은 야식을 추천하는 전문 챗봇입니다. {style} 사용자의 취향, 배고픔 정도, 시간, 알레르기 및 예산에 따라 1) 추천 메뉴 3가지, "
        "2) 각 메뉴에 대한 간단한 설명, 3) 추천 이유를 적어주고, 마지막에 사용자의 선호를 더 잘 알기 위해 덧붙여 물어볼 질문을 1개 추가하세요. 응답은 한국어로 해주세요."
    )

    # Display existing messages
    for msg in st.session_state.messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        with st.chat_message(role):
            st.markdown(content)

    # Chat input
    prompt = st.chat_input("무엇을 도와드릴까요? (예: '오늘 야식 추천해줘', '매운 걸 싫어해' 등)")
    if prompt:
        # Add the user's message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build messages for API (prepend system message)
        api_messages = [
            {"role": "system", "content": system_message},
        ] + [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]

        # Call OpenAI chat completion (non-streaming for stability)
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=api_messages,
                max_tokens=500,
                temperature=0.8,
            )
        except Exception as e:
            st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
        else:
            # Extract assistant content in a robust way (handles multiple SDK shapes)
            assistant_message = ""
            try:
                choice = response.choices[0]
                msg = getattr(choice, "message", None)
                if isinstance(msg, dict):
                    assistant_message = msg.get("content", "")
                elif hasattr(msg, "content"):
                    assistant_message = getattr(msg, "content", "")
                else:
                    # fallback to text attribute or to str(response)
                    assistant_message = getattr(choice, "text", "") or str(response)
            except Exception:
                try:
                    assistant_message = str(response)
                except Exception:
                    assistant_message = "(응답을 파싱할 수 없습니다.)"

            if assistant_message is None:
                assistant_message = "(응답이 비어있습니다.)"

            # Append and display assistant message
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
            with st.chat_message("assistant"):
                st.markdown(assistant_message)


if __name__ == "__main__":
    main()
