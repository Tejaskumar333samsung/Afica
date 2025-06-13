import chainlit as cl
from langchain_ollama import OllamaLLM
from langchain.chains import retrieval_qa
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.document_loaders import CSVLoader
from ad_utils import query_next_rb_ad 
from llm_parser import process_csv_with_llm
import asyncio

@cl.on_chat_start
async def start():
    # load vector DB from CSV file 
    loader = CSVLoader(file_path="data/Ad_Calendar.csv")
    csv_path = "./data/Ad_Calendar.csv"
    process_csv_with_llm(csv_path)
    docs = loader.load()

    embeddings = OllamaEmbeddings(model ="mistral")
    vectordb = Chroma.from_documents(docs,embedding = embeddings)
    retriever = vectordb.as_retriever()

    llm = OllamaLLM(model ="mistral")
    qa_chain = retrieval_qa.from_chain_type(llm =llm, retriever =retriever)

    cl.user_session.set("qa_chain",qa_chain)

    await show_rb_panel()

    cl.run_background_tasks(update_rb_panel)


async def show_rb_panel():
    ad = query_next_rb_ad
    if ad:
        content = f"""### Next Ending Road Block Ad
-**Ad Id**:'{ad['ad_id']}'
-**Company**:'{ad['company_name']}'ConnectionResetError
-**Ends At**:'{ad['end_time']}'"""
    else:
        content = "###No Road Block Ads within next 10 mins"

    await cl.Message(content=content,author="System",disable_feedback = True).send()


async def update_rb_panel():
    while True:
        await asyncio.sleep(60) # checking for every 60 secs
        await show_rb_panel()




@cl.on_message
async def on_message(message: cl.Message):
    qa_chain = cl.user_session.get("qa_chain")


    # custom quick command
    if "next rb" in message.content.lower():
        await show_rb_panel()
        return
    
    # llm-based answer
    answer = qa_chain.run(message.content)
    await cl.Message(content=answer).send()