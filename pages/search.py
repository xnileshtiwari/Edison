import streamlit as st
import google.generativeai as genai
from google.oauth2.credentials import Credentials
import time





  generation_config = {
  "temperature": 0.2,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
  }



def edison(input):  
  
  model = genai.GenerativeModel(
  model_name= st.secrets["api_keys"]["model"], apikey = st.secrets["api_keys"]["gemini"],
  generation_config=generation_config,
  )
  
  # Generate text
  response = model.generate_content(input)
  return response.text







def stream_data(input):
    for word in input.split(" "):
        yield word + " "
        time.sleep(0.03)







# Center the toggle
st.empty()
col1, col2, col3 = st.columns(3)
with col1:
    st.empty()
with col2:
    on = st.toggle("Activate Edison")

    if on:
        st.title("Edison🌱")

    else:
        st.title("Default🔎")

with col3:
    st.empty()


if on:
    st.write("AI assistant aligned towards promoting sustainability🌍")



# Pre-written questions
pre_written_questions = [
    "Choose prompts",
    "How can i become a good individual?",
    "Recipes And Cooking Tips",
    "Tips for a well-balanced diet",
    "I want to fly first-class from Miami to Dubai.",
    "What’s the fastest flight from Chicago to San Francisco?",
    "Looking for a round-trip flight from Sydney to Melbourne."
]









def normal(input):
    genai.configure(api_key=st.secrets['api_keys']['gemini'])

    model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)

    response = model.generate_content(input)
    return response.text












with st.form("my_form", clear_on_submit=True):
    selected_question = st.selectbox(
    "Choose a pre-written prompt to test:",
    options=pre_written_questions)
    
    user = st.text_input("What do you have on your mind?", key="Edison",placeholder="Type something...")

    submitted = st.form_submit_button("Submit")


if submitted:
    theater = user if user else selected_question

    if on:
        st.write(f'Query: {theater}')
        with st.spinner("Generating..."):
            emo = edison(theater)
        st.write_stream(stream_data(emo))
    else:
        st.write(f'Query: {theater}')
        with st.spinner("Generating..."):
            normal_text = normal(theater)
        st.write_stream(stream_data(normal_text))


