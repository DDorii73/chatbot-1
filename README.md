# 💬 야식 추천 챗봇

Streamlit 앱으로 구현한 간단한 챗봇입니다. OpenAI GPT 모델(gpt-4o-mini)을 사용해 사용자의 선호에 맞춰 야식 메뉴를 추천합니다. 이 앱은 API 키를 `./.streamlit/secrets.toml`에 저장해 자동으로 불러옵니다.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Configure your OpenAI API key

   Create `.streamlit/secrets.toml` and add your API key like:

   ```toml
   OPENAI_API_KEY = "sk-..."
   ```

3. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
