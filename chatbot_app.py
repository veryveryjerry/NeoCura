import streamlit as st
import requests
import json

# Configure Streamlit page
st.set_page_config(
    page_title="NeoCura Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Backend URL
BACKEND_URL = "https://neocura.onrender.com/webhook"

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Title and description
st.title("🤖 NeoCura Chatbot")
st.markdown("Ask me anything and I'll help you with your questions!")

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
st.sidebar.write(f"Selected: {lang_display[language]}")

# Chat interface
st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare payload for backend
    payload = {
        "message": prompt,
        "language": language.lower(),
        "user_id": "streamlit_user",
        "timestamp": str(st.session_state.get('timestamp', ''))
    }
    
    try:
        # Send request to Flask backend
        with st.spinner("Thinking..."):
            response = requests.post(
                BACKEND_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
        
        if response.status_code == 200:
            # Parse response
            bot_response = response.json()
            bot_message = bot_response.get('response', 'Sorry, I could not process your request.')
            
            # Add bot response to chat history
            st.session_state.messages.append({"role": "assistant", "content": bot_message})
            
            # Display bot response
            with st.chat_message("assistant"):
                st.markdown(bot_message)
        else:
            error_msg = f"Error: Server responded with status {response.status_code}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
            with st.chat_message("assistant"):
                st.error(error_msg)
    
    except requests.exceptions.Timeout:
        error_msg = "Request timed out. Please try again."
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        with st.chat_message("assistant"):
            st.error(error_msg)
    
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        with st.chat_message("assistant"):
            st.error(error_msg)
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        with st.chat_message("assistant"):
            st.error(error_msg)

# Clear chat button
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>NeoCura Chatbot | Powered by Streamlit</p>
        <p>Start command for Render deployment: <code>streamlit run chatbot_app.py</code></p>
    </div>
    """,
    unsafe_allow_html=True
)
