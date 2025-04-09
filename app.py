import streamlit as st
from agents.controller import ControllerAgent
from PIL import Image

# Initialize controller
controller = ControllerAgent()

try:
    logo = Image.open("ask-me-data-logo.jpeg")  # Updated to your logo file
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image(logo, width=150, caption="", use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Error loading logo: {e}")
    
# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Enter your MongoDB command (e.g., 'Insert a user named John into collection users')"):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Process the prompt and get response
    with st.chat_message("assistant"):
        response = controller.create_execution_plan(prompt, st.session_state)
        st.write(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.session_state.pop("pending_clarification", None)
    st.rerun()