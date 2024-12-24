import streamlit as st
import utils
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import json
import pickle

# Streamlit UI
st.title("Gmail Spam Email Viewer")
df_email = pd.DataFrame()
text_cloud = ""
wordcloud = WordCloud()
with open("keys/openai.json", 'r') as file:
    data = json.load(file)
openai_api_key = data['openai_api_key']
#input = ""
output = ""
num_emails = 0


# Login Button
if st.button("Authenticate & Connect Gmail"):
    try:
        service = utils.authenticate_user()
        st.success("Authentication successful!")
    except Exception as e:
        st.error(f"Authentication failed: {e}")

num_emails=st.number_input(label="How many emails?",min_value=1, max_value=30)

if st.button("Fetch Spam Emails and Generate WordCloud"):
    try:
        service = utils.authenticate_user()
        spam_emails, df_email, text_cloud = utils.fetch_spam_emails(service, results=num_emails)
        if spam_emails:
            st.write("### Spam Emails:")
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text_cloud)

            # Display the WordCloud using Matplotlib
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")

            st.pyplot(fig)
        else:
            st.write("No spam emails found.")
        if not df_email.empty:
            with open('df.pkl', 'wb') as df_file:
                pickle.dump(df_email,df_file)
    except Exception as e:
        st.error(f"Error fetching spam emails: {e}")

if st.button("Summarizing emails"):
    print(df_email.head())
    try:
        service = utils.authenticate_user()
        with open('df.pkl', 'rb') as df_file:
            df_email = pickle.load(df_file)
    
        output = utils.summary_gpt(df_email, api_key=openai_api_key)
        st.dataframe(output)
    except Exception as e:
        st.error(f"Error fetching spam emails: {e}")
    