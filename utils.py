import streamlit as st
import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import ast

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_user():
    """Authenticate user and return Gmail API service."""
    creds = None
    if os.path.exists('token.pkl'): # Load credentials if they exist
        with open('token.pkl', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:  # If no valid credentials, let's authenticate
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('keys/desktop.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pkl', 'wb') as token: # Save credentials
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def fetch_spam_emails(service, results):
    """Fetch emails from the Spam folder."""
    messages = []
    try:
        # Use the Gmail API to search for emails in the Spam folder
        response = service.users().messages().list(userId='me', labelIds=['SPAM'], maxResults=results).execute()
        messages = response.get('messages', [])
    except Exception as e:
        st.error(f"Error fetching emails: {e}")

    emails = []
    for message in messages:
        try:
            msg_data = service.users().messages().get(userId='me', id=message['id']).execute()
            snippet = msg_data.get('snippet', '(No snippet available)')
            emails.append(snippet)
        except Exception as e:
            st.error(f"Error fetching email details: {e}")
    
    df_email = pd.DataFrame(emails, columns=['email'])
    text = " ".join(str(value) for value in df_email['email'])
    return emails, df_email, text


def summary_gpt(df: pd.DataFrame,  api_key):

    prompt = PromptTemplate(input_variables=["text"], template= "Summarize this emails: {text} and returns as a dictionary")

    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0,
        max_tokens=4096,
        openai_api_key=api_key
    )

    transaction_chain = LLMChain(
        llm=llm,
        prompt=prompt
    )

    text_input = df.to_dict()['email']
    text_output = transaction_chain.predict(text = text_input)
    data_dict = ast.literal_eval(text_output.strip())
    df_output = pd.DataFrame(list(data_dict.items()), columns=['Index', 'Summary'])
    df_output = df_output.set_index('Index')
    return df_output
    