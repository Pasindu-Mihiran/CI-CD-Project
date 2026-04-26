import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

st.set_page_config(page_title="Hugging Face Chatbot", layout="wide")
st.title("🤖 Chatbot with Context Memory (DialoGPT)")

# Constants
MAX_TOKENS = 1000  # Change based on model max length
HISTORY_ROUNDS = 6  # Keep last N exchanges

# Load model & tokenizer
@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")
    model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")
    return tokenizer, model

tokenizer, model = load_model()

# Initialize session state
if "chat_history_ids" not in st.session_state:
    st.session_state.chat_history_ids = None
if "conversation" not in st.session_state:
    st.session_state.conversation = []  # Stores (user_input, bot_response)

# Reset button
if st.button("🧹 Clear Chat"):
    st.session_state.chat_history_ids = None
    st.session_state.conversation = []
    st.experimental_rerun()

# Input
user_input = st.text_input("You:", key="input")

if user_input:
    # Encode user input
    new_input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")

    # Rebuild recent chat history if needed
    if st.session_state.conversation:
        chat_tokens = []
        for user, bot in st.session_state.conversation[-HISTORY_ROUNDS:]:
            chat_tokens += tokenizer.encode(user + tokenizer.eos_token, return_tensors="pt")[0].tolist()
            chat_tokens += tokenizer.encode(bot + tokenizer.eos_token, return_tensors="pt")[0].tolist()
        chat_tokens += new_input_ids[0].tolist()
        chat_tokens = chat_tokens[-MAX_TOKENS:]  # Trim oldest tokens
        bot_input_ids = torch.tensor([chat_tokens])
    else:
        bot_input_ids = new_input_ids

    # Generate response
    output_ids = model.generate(
        bot_input_ids,
        max_length=bot_input_ids.shape[-1] + 100,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.8,
    )

    # Extract new response
    response = tokenizer.decode(output_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

    # Save conversation
    st.session_state.conversation.append((user_input, response))

    # Display chat
    for i, (user, bot) in enumerate(st.session_state.conversation[-HISTORY_ROUNDS:]):
        st.markdown(f"**You:** {user}")
        st.markdown(f"**Bot:** {bot}")