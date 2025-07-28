import streamlit as st
from datetime import date

st.title("😊 Daily Mood Tracker")

# Initialize session state
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# Mood options
mood = st.selectbox("How do you feel today?", ["😀 Happy", "😐 Neutral", "😔 Sad", "😡 Angry", "😴 Tired"])
note = st.text_area("Any notes about your day?")

if st.button("📌 Save Mood"):
    st.session_state.mood_log.append({
        "date": str(date.today()),
        "mood": mood,
        "note": note
    })
    st.success("Mood saved!")

st.subheader("📅 Mood History")
for entry in reversed(st.session_state.mood_log):
    st.write(f"**{entry['date']}** - {entry['mood']}")
    if entry['note']:
        st.write(f"> {entry['note']}")

