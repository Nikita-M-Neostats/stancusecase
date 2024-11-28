#  Using pandas AI

from pandasai import SmartDatalake
import streamlit as st
import pandas as pd
from langchain import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
import warnings
warnings.filterwarnings("ignore")
import regex as re
import time
import pyodbc
from streamlit.web.server import Server
from pandasai import SmartDatalake
import os

class SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

api_version=st.secrets.api_version
model=st.secrets.model
api_key=st.secrets.api_key
azure_endpoint=st.secrets.azure_endpoint       
server = st.secrets.server  # Azure SQL server name
database = st.secrets.database  # Database name
username = st.secrets.username  # Azure SQL username
password = st.secrets.password  # Azure SQL password
driver = '{ODBC Driver 17 for SQL Server}'  # Driver for Azure SQL
connectionstring = f"Driver={driver};Server=tcp:genailabssqlserver.database.windows.net,1433;Database=talk2data;Uid=genailabsqluser;Pwd={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

llm = AzureChatOpenAI(
    api_version=api_version,
    model=model,
    temperature=0,
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    )
def get_session_state(**kwargs):
    session = getattr(st, '_session_state', None)
    if session is None:
        session = SessionState(**kwargs)
        setattr(st, '_session_state', session)
    for key, val in kwargs.items():
        if not hasattr(session, key):
            setattr(session, key, val)
    return session

def get_table_info():
    try:
        # Connect to the database
        conn = pyodbc.connect(connectionstring)
        cursor = conn.cursor()

        cursor.execute(f"SELECT TOP 5 * FROM Customer_Data")
        records = cursor.fetchall()
        columns = [column[0] for column in cursor.description]  # Get column names
        df = pd.DataFrame.from_records(records, columns=columns)
        st.dataframe(df.style.hide(axis="index"))
        return df
    except Exception as e:
        st.error("Error executing query: " + str(e))

def openai_model(question):
    start_time = time.time()
    template = '''
        YOU ARE SQL EXPERT THAT SPECIALIZES IN SQL CODE GENERATION.
        GENERATE SQL QUERY FOR THE USER QUESTION {question}.
        MAKE SURE YOUR RESPONSE SHOULD CONTAIN JUST CORRECT SQL QUERY. DO NOT GIVE EXPLANATION OR ANY OTHER INSTRUCTION.
        MAKE SURE THAT GENERATED SQL QUERY SHOULD BE IN PROPER FORMAT AND USE PROPER SQL SYNTAX. 
        DO NOT INCLUDE sql KEYWORD IN YOUR RESPONSE.
    '''
    prompt = PromptTemplate(
                        template=template,
                        input_variables=["question"]
                        )
    chain = LLMChain(prompt=prompt, llm=llm)
    answer = chain.run({
                'question': question,
            })
    print("raw answer",answer)
    end_time = time.time()
    execution_time = end_time - start_time
    st.write("Query Generation time :",round(execution_time,2))
    replace_words = ["\\*","sql","```"]
    for keyword in replace_words:
        answer = answer.replace(keyword," ")
    return answer

def execute_query(query):
    try:
        conn = pyodbc.connect(connectionstring)
        cursor = conn.cursor()
        cursor.execute(query)
        if 'SELECT' in query.strip().upper():
            records = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame.from_records(records, columns=columns)
            st.dataframe(df)
            cursor.close()
            conn.close()
            return df
        else:
            conn.commit()
            cursor.close()
            conn.close()
            st.write("Query Executed Successfully")
            return "Query Executed Successfully"
    except Exception as e:
        print("Error executing query: " + str(e))

def main():
    st.set_page_config (
        page_title="Home",
        page_icon="👋",
        layout = "wide"
    )
    response = None
    res = None
    session_state = get_session_state(df=pd.DataFrame, column_list=[], llm_response=None, visual_response=None)  
    st.image("image.png", use_column_width=False) 
    st.title('IntelliSQL: AI-Enhanced NL to SQL Generation')
    with st.container(border=True):
        col1, col2= st.columns([0.3, 0.7])
        with col1:
            with st.container(border=True,height=300):
                selected_table="Customer_Data"
                st.write("Table Name: Customer_Data")
        with col2:
            with st.container(border=True,height=300):
                st.subheader(f'Sample Records of Customer_Data')
                s=get_table_info()
                print(s)

        col1, col2= st.columns([0.3, 0.7])
        with col1:
            with st.container(border=True,height=400):
                question = st.text_area('Enter your Query')
                if st.button("Generate", type="primary"):
                    if question:
                        response = openai_model(question)
                        session_state.llm_response = response
                        st.write('Response Generated by LLM:')
                        st.code(session_state.llm_response)
        with col2:
            with st.container(border=True,height=400):
                st.subheader('Result')
                session_state.df = execute_query(session_state.llm_response)
        col1, col2= st.columns([0.3, 0.7])
        if session_state.df is not None:
            with col1:
                with st.container(border=True,height=400):
                    que = st.text_area('Enter your question for visuals')
                    if st.button("Show"):
                        if que is not None:
                            with col2:
                                with st.container(border=True,height=400):
                                    st.subheader('Result')
                                    lake = SmartDatalake(session_state.df, config={"llm": llm})
                                    res = lake.chat(que)
                                    try:
                                        if res is not None:
                                            if isinstance(res, str):
                                                if os.path.exists(res) and re.match(r".*\.(jpg|jpeg|png|gif)$", res, re.IGNORECASE):
                                                    with st.container(border=True, height=600):
                                                        st.image(res, use_column_width=True)
                                                else:
                                                    with st.container(border=True, height=300):
                                                        st.write(res)
                                            elif isinstance(res, pd.DataFrame):
                                                with st.container(border=True, height=600):
                                                    st.dataframe(res)
                                        else:
                                            with st.container(border=True, height=300):
                                                st.text("No response available.")
                                    except Exception as e:
                                        print("error:", str(e))
            

if __name__ == '__main__':
    main()
