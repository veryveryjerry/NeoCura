import streamlit as st
import requests
import json

# Configure Streamlit page
st.set_page_config(
    page_title="NeoCura Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Backend URL - Changed to use /analyze endpoint instead of /webhook
BACKEND_URL = "https://neocura.onrender.com/analyze"

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
    
    # Store timestamp
    import datetime
    st.session_state.timestamp = datetime.datetime.now().isoformat()
    
    # Prepare payload for /analyze endpoint
    payload = {
        "text": prompt,
        "language": language.lower()
    }
    
    try:
        # Send request to backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # =====================================================
                # 🚨🚨🚨 ABOUT TO SEND BACKEND API REQUEST 🚨🚨🚨
                # =====================================================
                print("\n" + "=" * 60)
                print("🚀 BACKEND API CALL STARTING")
                print(f"📍 URL: {BACKEND_URL}")
                print(f"📦 Payload: {payload}")
                print(f"🕐 Timestamp: {datetime.datetime.now()}")
                print("=" * 60 + "\n")
                
                response = requests.post(
                    BACKEND_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    bot_response = result.get('response', 'Sorry, I could not generate a response.')
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    st.markdown(bot_response)
                    
                    # =====================================================
                    # ✅✅✅ SUCCESSFUL API RESPONSE RECEIVED ✅✅✅
                    # =====================================================
                    print("\n" + "=" * 60)
                    print("✅ BACKEND API CALL SUCCESSFUL")
                    print(f"📊 Status Code: {response.status_code}")
                    print(f"📄 Response Length: {len(bot_response)} characters")
                    print(f"🕐 Completed at: {datetime.datetime.now()}")
                    print("=" * 60 + "\n")
                    
                else:
                    error_msg = f"Error: {response.status_code} - {response.text}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.error(error_msg)
                    
                    # =====================================================
                    # ❌❌❌ API ERROR RESPONSE RECEIVED ❌❌❌
                    # =====================================================
                    print("\n" + "=" * 60)
                    print("❌ BACKEND API CALL FAILED")
                    print(f"📊 Status Code: {response.status_code}")
                    print(f"📄 Error Message: {response.text}")
                    print(f"🕐 Failed at: {datetime.datetime.now()}")
                    print("=" * 60 + "\n")
                    
    except requests.exceptions.RequestException as e:
        error_msg = f"Connection error: {str(e)}"
        with st.chat_message("assistant"):
            st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # =====================================================
        # 🔌🔌🔌 CONNECTION ERROR OCCURRED 🔌🔌🔌
        # =====================================================
        print("\n" + "=" * 60)
        print("🔌 CONNECTION ERROR")
        print(f"📄 Error: {str(e)}")
        print(f"🕐 Error at: {datetime.datetime.now()}")
        print("=" * 60 + "\n")
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        with st.chat_message("assistant"):
            st.error(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # =====================================================
        # 💥💥💥 UNEXPECTED ERROR OCCURRED 💥💥💥
        # =====================================================
        print("\n" + "=" * 60)
        print("💥 UNEXPECTED ERROR")
        print(f"📄 Error: {str(e)}")
        print(f"🕐 Error at: {datetime.datetime.now()}")
        print("=" * 60 + "\n")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** You can ask questions in English, Hindi, or Odia!")
st.markdown("🔗 **Powered by:** NeoCura AI Assistant")
