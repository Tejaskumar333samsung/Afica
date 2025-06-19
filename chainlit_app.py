import chainlit as cl
from langchain_ollama import OllamaLLM
# from langchain.chains import RetrievalQA as retrieval_qa
# from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import OllamaEmbeddings
# from langchain_community.document_loaders import CSVLoader
from ad_utils import query_next_rb_ad, is_ad_table_empty, fetch_upcoming_ads
from llm_parser import process_csv_with_llm
import asyncio
import json
from datetime import datetime
import pandas as pd

df = pd.read_csv("./data/Ad_Calendar.csv")
csv_data = df.to_dict(orient='records')
csv_content = json.dumps(csv_data, ensure_ascii=False)
# loader = CSVLoader(file_path="./data/Ad_Calendar.csv")
# # csv_path = "./data/Ad_Calendar.csv"
# # process_csv_with_llm(csv_path)
# # docs = loader.load()

# # loader = DataFrameLoader(df)
# docs = loader.load()

# # Proceed with vector DB setup for Q&A
# embeddings = OllamaEmbeddings(model ="mistral")  #deepseek-r1:7b
# vectordb = Chroma.from_documents(docs,embedding = embeddings)
# retriever = vectordb.as_retriever()

llm = OllamaLLM(model ="mistral")

async def update_rb_panel():
    while True:
        await asyncio.sleep(120)  # every 2 minutes
        # include real time in header
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        panel = await show_rb_panel(return_only=True)
        await cl.Message(
            content=f"⌛ {now}\n\n" + panel,
            author="System",
            # disable_feedback=True,
        ).send()


@cl.on_chat_start
async def start():

    res = await cl.AskUserMessage(content="do you want to upload a new csv file ?(y/n)", timeout=50).send()
    # print(res)
    # print(type(res))  # dictionary
    # print(res["output"])
    # print(type(res["output"]))
    # print(str(res)[4]) 
    if res :
        print("got y/n res\n")
        if str(res["output"]) == "y":
            print("entered y \n")
            # await cl.Message(
            #     content=f"Your name is: {res['output']}",
            # ).send()
            files = None
            while files is None:
                files = await cl.AskFileMessage(content="Please upload a csv file to begin!", accept=["csv"]).send()
                csv_file = files[0]
            df1 = pd.read_csv(csv_file.path)
            csv_data1 = df1.to_dict(orient='records')
            csv_content1 = json.dumps(csv_data1, ensure_ascii=False)
            print("processing uploaded calendar with llm\n")
            process_csv_with_llm(df1)

            msg = None
            while msg is None:
                # print("entered y while msg is none \n")
                msg = await cl.AskUserMessage(content="Any query from the uploaded ad calender?",timeout=100000).send()
                if msg:
                    while msg is not None and str(msg["output"]) != "bye":
                        if msg:
                            # print("entered while != bye loop in on message\n")
                            print(f"user : {msg['output']}\n")

                            #{csv_content},
                            prompt = f"""
                            You are ad calendar manager, with calendar data : {csv_content1},    
                            User asked: "{msg['output']}"
                            Please provide an answer in based on that given data.
                            """
                            response = llm.invoke(prompt)
                            print("response from llm invoke function in on message\n")
                            # print("response from llm parser function after n\n")
                            await cl.Message(content=f"AFICA: {response}", author="System").send()
                            msg = await cl.AskUserMessage(content="Anything more? or say bye to end",timeout=100000).send()

                    await cl.Message(content = "bye").send()
                # if msg:
                #     prompt = f"""
                #     You are ad calendar manager, with calendar data: {csv_content1},
                #     client asked: "{msg['output']}"
                #     Please provide an answer based on this data.
                #     """
                #     response = llm.invoke(prompt)
                #     await cl.Message(content=response).send()
            # print("exited y while msg is none \n")
            # loader = DataFrameLoader(df)
            # loader = CSVLoader(file_path=csv_file.path)
            # docs = loader.load()
            # # Proceed with vector DB setup for Q&A
            # # embeddings = OllamaEmbeddings(model ="mistral")  #deepseek-r1:7b
            # vectordb1 = Chroma.from_documents(docs,embedding = embeddings)
            # retriever1 = vectordb1.as_retriever()
            # # llm = OllamaLLM(model ="mistral")
            
            # qa_chain = retrieval_qa.from_chain_type(llm =llm, retriever =retriever1)
            
            # cl.user_session.set("qa_chain",qa_chain)
            # Now display the next ending Rb ad immediately
            # await show_rb_panel(True)

        elif str(res["output"]) == "n":
            print("entered n\n")
            if is_ad_table_empty():
                await cl.Message(
                    content="ℹ️ Ad table is missing or empty—parsing CSV and populating database…",
                    author="System",
                    # disable_feedback=True,
                ).send()
                print("table is empy, processing local csv with llm\n")
                process_csv_with_llm(df)

            msg = None
            while msg is None:
                # print("entered n while msg is none \n")
                msg = await cl.AskUserMessage(content="Any query from the ad calender?",timeout=100000).send()
                if msg:
                    while msg is not None and str(msg["output"]) != "bye":
                        # print("entered while != bye loop in on message\n")
                        print(f"user : {msg['output']}\n")
                        #{csv_content},
                        prompt = f"""
                        You are ad calendar manager, with calendar data : {csv_content},    
                        User asked: "{msg['output']}"
                        Please provide an answer in based on that given data.
                        """
                        response = llm.invoke(prompt)
                        print(f"AFICA: {response}")
                        # print(type(response))
                        print("response from llm invoke function in on message\n")
                        # print("response from llm parser function after n\n")
                        await cl.Message(content=f"{response}",  author="System").send()
                        msg = await cl.AskUserMessage(content="Anything more? or say bye to end",timeout=100000).send()
                        

                    await cl.Message(content = "bye").send()


                # if msg:
                #     prompt = f"""
                #     You are ad calendar manager, with calendar data: {csv_content},
                #     client asked: "{msg['output']}"
                #     Please provide an answer based on this data.
                #     """
                #     response = llm.invoke(prompt)
                #     print(response)
                #     print("response from llm parser function after n\n")
                #     await cl.Message(content=response).send()
            # print("exited n while msg is none \n")
            # qa_chain = retrieval_qa.from_chain_type(llm =llm, retriever =retriever)
            # cl.user_session.set("qa_chain",qa_chain)

            
            # Now display the next ending Rb ad immediately
            # await show_rb_panel(True)
        
        else:
            await cl.Message( content="Invalid input. Please respond with 'y' or 'n'.", author="System").send()

        # cl.run_background_tasks(update_rb_panel)

    




@cl.on_message
async def on_message(message: cl.Message):
    # qa_chain = cl.user_session.get("qa_chain")
    if message.content not in ("y", "n","bye"):
        print("entered on normal message\n")
        #: {csv_content}
        prompt = f"""
        You are ad calendar manager, with calendar data : {csv_content},
        User asked: "{message.content}"
        Please provide an answer in based on that given data.
        """
        response = llm.invoke(prompt)
        print("response from llm invoke function in on message\n")
        await cl.Message(content=f"AFICA: {response}", author = "system").send()

        msg = await cl.AskUserMessage(content="Anything more ? send bye to end",timeout=100000).send()
        if msg:
            while msg is not None and str(msg["output"]) != "bye":
                print("entered while != bye loop in on message\n")
                #{csv_content},
                prompt = f"""
                You are ad calendar manager, with calendar data : {csv_content},    
                User asked: "{msg['output']}"
                Please provide an answer in based on that given data.
                """
                response = llm.invoke(prompt)
                print("response from llm invoke function in on message\n")
                # print("response from llm parser function after n\n")
                await cl.Message(content=f"{response}",  author="System").send()
                msg = await cl.AskUserMessage(content="Anything more? or say bye to end",timeout=100000).send()

            await cl.Message(content = "bye").send()



    # # custom quick command
    # if "next rb" in message.content.lower():
    #     await show_rb_panel()
    #     return

    # if not is_ad_table_empty():
    #     # Prepend a small “tools” context: next 3 upcoming ads
    #     upcoming = fetch_upcoming_ads(limit=3)
    #     context = "Upcoming Ads:\n" + "\n".join(
    #         f"- {a['ad_id']} (ends {a['end_time']})" for a in upcoming
    #     ) + "\n\n"
    #     answer = qa_chain.run(context + message.content)
    #     await cl.Message(content=answer).send()
    # answer = qa_chain.run(message.content)
    # await cl.Message(content=answer).send()

async def show_rb_panel(return_only):
   ad = query_next_rb_ad()
   if ad:
        content = (
            "### Next Ending Road Block Ad\n"
            f"- **Ad Id**: {ad['ad_id']}\n"
            f"- **Company**: {ad['company_name']}\n"
            f"- **Ends At**: {ad['end_time']}"
        )
   else:
        content = "### No Road Block Ads within next 10 mins"

   if return_only:
        return content

   await cl.Message(content=content, author="System").send() #disable_feedback=True    