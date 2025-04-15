import streamlit as st
import google.generativeai as genai
import time




# Configure Gemini ONCE at app startup
genai.configure(api_key=st.secrets["gemini"])  # Use api_key, not apikey

normal_model = "gemini-1.5-flash"



# Initialize the model ONCE outside the function
model = genai.GenerativeModel(normal_model)  # Use the model_name

generation_config = {
  "temperature": 0.2,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model_name = "tunedModels/gemini1-gcj8te79ymew"



def edison(input):  
    model = genai.GenerativeModel(model_name)  # Use the model_name


    response = model.generate_content(input, generation_config=generation_config, stream=True)  # Add generation_config here.
    full_text = "".join([chunk.text for chunk in response])
    return full_text



  




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
    model = genai.GenerativeModel(normal_model)  # Use the model_name

    #  genai is ALREADY configured, and model is ALREADY instantiated
    response = model.generate_content(input, generation_config=generation_config, stream=True)  # Add generation_config here.
    full_text = "".join([chunk.text for chunk in response])
    return full_text












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


