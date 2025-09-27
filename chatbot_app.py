import streamlit as st
import os
from openai import OpenAI

# Configure Streamlit page
st.set_page_config(
    page_title="NeoCura Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Initialize OpenAI client with HuggingFace Router
client = OpenAI(
    base_url="https://api.endpoints.huggingface.cloud/v2/openai",  # HuggingFace Router as base_url
    api_key=os.getenv("HF_TOKEN")
)

# Model configuration
MODEL = "m42-health/Llama3-Med42-70B:featherless-ai"

def analyze_query(user_input):
    """Call /analyze API using OpenAI client"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are NeoCura, a helpful medical assistant. Provide accurate and helpful responses to medical questions while being empathetic and professional."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Title and description
st.title("🤖 NeoCura Chatbot")
st.markdown("Ask me anything and I'll help you with your medical questions!")

# Language selection
st.sidebar.header("Settings")
language = st.sidebar.selectbox(
    "Choose Language / भाषा चुनें / ଭାଷା ବାଛନ୍ତୁ",
    options=["English", "Hindi", "Odia"],
    index=0
)

# Display language confirmation
lang_display = {
    "English": "🇺🇸 English",
    "Hindi": "🇮🇳 हिंदी",
    "Odia": "🇮🇳 ଓଡ଼ିଆ"
}
st.sidebar.success(f"Selected: {lang_display[language]}")

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = analyze_query(prompt)
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
