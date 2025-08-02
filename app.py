import streamlit as st
import requests
from database.db import init_database, insert_chat_message, get_chat_history

# Function to get response from the backend API
def chatbot_response(input_text):
    url = 'https://avid-infinity-386618.el.r.appspot.com/api'
    payload = {'userPrompt': input_text}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'privatePrompt': f"Error: {str(e)}"}

# Display chat history from DB (used in sidebar)
def display_chat_history(chat_history):
    st.subheader("Chat History (from DB)")
    chat_container = st.empty()
    chat_log = ""
    for sender, message in chat_history:
        style = "#333" if sender == "You" else "#555"
        chat_log += f'<div style="padding: 1rem; margin-bottom: 5px; color:#fff; background-color: {style}; border-radius: 8px;">{sender}: {message}</div>'
    chat_container.markdown(chat_log, unsafe_allow_html=True)

# Clear session chat history
def clear_chat_history():
    st.session_state.chat_history = []

# MAIN APP
def main():
    st.set_page_config(page_title="Private GPT", layout="centered")

    st.title("🤖 Private GPT")

    # Initialize DB
    if not init_database():
        st.error("Failed to connect to the database.")
        st.stop()

    # Load previous history from session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar
    st.sidebar.title("⚙️ Settings")
    if st.sidebar.button("🕘 Show DB Chat History"):
        db_history = get_chat_history()
        display_chat_history(db_history)

    if st.sidebar.button("🗑️ Clear Session History"):
        clear_chat_history()

    # Text input and send button
    user_input = st.text_input("You:", key="text_input")
    if st.button("Send"):
        if user_input.strip() == "":
            st.warning("Please enter a message.")
        else:
            response_data = chatbot_response(user_input)
            bot_reply = response_data.get("privatePrompt", "Sorry, no response.")

            # Save to session and DB
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("PrivateGPT", bot_reply))
            insert_chat_message("You", user_input)
            insert_chat_message("PrivateGPT", bot_reply)

            # Clear input
            st.session_state.text_input = ""

    # Display current chat session
    st.subheader("Live Chat")
    chat_display = ""
    for sender, message in st.session_state.chat_history:
        style = "#333" if sender == "You" else "#555"
        chat_display += f'<div style="padding: 1rem; margin-bottom: 5px; color:#fff; background-color: {style}; border-radius: 8px;">{sender}: {message}</div>'
    st.markdown(chat_display, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
