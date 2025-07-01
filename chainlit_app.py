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
    res = await cl.AskUserMessage(content="do you want to upload a new csv file ?(y/n)", timeout=10).send()
    if res :
        # print("got y/n res\n")
        if str(res["output"]) == "y":
            # print("entered y \n")
            # files = None
            # while files is None:
            files = await cl.AskFileMessage(content="Please upload a csv file to begin!",timeout=100, accept=["text/csv",".csv"],raise_on_timeout=True).send()
            csv_file = files[0]
            df1 = pd.read_csv(csv_file.path)
            csv_data1 = df1.to_dict(orient='records')
            csv_content1 = json.dumps(csv_data1, ensure_ascii=False)
            print("\nprocessing uploaded calendar with llm\n")
            process_csv_with_llm(csv_data1)
            print("\n uploaded calendar processed \n")
            # msg = None
            # while msg is None:
                # print("entered y while msg is none \n")
            print("user info : x" ,cl.user_session)
            msg1 = await cl.AskUserMessage(content="Any query from the uploaded ad calender?",timeout=500,raise_on_timeout=True).send()
            print(msg1)
            print("user info : y" ,cl.user_session)

            print(f"{msg1['output']}\n")
            # while msg is None:
            #     continue
            while ((msg1 is not None) and (str(msg1["output"]) != "bye")):
                print("entered while != bye loop in on message\n")
                current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"user : {msg1['output']}\n")

                #{csv_content},
                prompt = f"""
                You are a friendly ad calendar manager, with calendar data : {csv_content1},    
                User asked: "{msg1['output']}"
                Please provide precise answer in concise way based on that given data, also know that current date,time is {current_date_time}.
                """
                response = llm.invoke(prompt)
                print(f"\n AFICA: {response}\n")
                print("\nresponse from llm invoke function in on message\n")
                # print("response from llm parser function after n\n")
                await cl.Message(content=f"{response}", author="System").send()
                msg1 = await cl.AskUserMessage(content="Anything more? or say bye to end").send()
                # while msg is None:
                #     continue                    
            print("\nbye\n")
            await cl.Message(content = "bye").send()

        elif str(res["output"]) == "n":
            # print("entered n\n")
            if is_ad_table_empty():
                await cl.Message(content="Ad table is missing or empty, parsing CSV and populating database…",author="System").send()
                print("\ntable is empty, processing local csv with llm\n")
                process_csv_with_llm(csv_data)
            msg = None
            while msg is None:
                # print("entered n while msg is none \n")
                msg = await cl.AskUserMessage(content="Any query from the ad calender?",timeout=100).send()
                if msg:
                    while msg is not None and str(msg["output"]) != "bye":
                        # print("entered while != bye loop in on message\n")
                        print(f"\nuser : {msg['output']}\n")
                        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #{csv_content},
                        prompt = f"""
                        You are a friendly ad calendar manager, with calendar data : {csv_content},    
                        User asked: "{msg['output']}"
                        Please provide precise answer in concise way based on that given data, also know current date,time is {current_date_time}.
                        """
                        response = llm.invoke(prompt)
                        print(f"\n AFICA: {response}\n")
                        # print(type(response))
                        print("\nresponse from llm invoked as message\n")
                        # print("response from llm parser function after n\n")
                        await cl.Message(content=f"{response}",  author="System").send()
                        msg = await cl.AskUserMessage(content="Anything more? or say bye to end",timeout=100).send()    
                    print("\nbye\n")
                    await cl.Message(content = "bye").send()
        
        else:
            print("\n invalid input at y/n \n")
            await cl.Message( content=f"Invalid input. Please respond with 'y' or 'n'.", author="System").send()

        # cl.run_background_tasks(update_rb_panel)

    




@cl.on_message
async def on_message(message: cl.Message):
    # qa_chain = cl.user_session.get("qa_chain")
    if message.content not in ("y", "n","bye"):
        print("\n normal message\n")
        print(f"\nuser : {message.content}\n")
        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #: {csv_content}
        prompt = f"""
        You are friendly ad calendar manager, with calendar data : {csv_content},
        User asked: "{message.content}"
        Please provide precise answer in concise way based on that given data, also know that current date,time is {current_date_time}.
        """
        response = llm.invoke(prompt)
        print(f"\n AFICA: {response}\n")
        print("\nresponse from llm invoked as message\n")
        await cl.Message(content=f"{response}", author = "system").send()

        msg = await cl.AskUserMessage(content="Anything more ? send bye to end",timeout=100000).send()
        if msg:
            while msg is not None and str(msg["output"]) != "bye":
                # print("entered while != bye loop in on message\n")
                print(f"\nuser : {msg['output']}\n")
                current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                #{csv_content},
                prompt = f"""
                You are a friendly ad calendar manager, with calendar data : {csv_content},    
                User asked: "{msg['output']}"
                Please provide precise answer in concise way based on that given data, also know that current date,time is {current_date_time}.
                """
                response = llm.invoke(prompt)
                print(f"\n AFICA: {response}\n")
                print("\nresponse from llm invoked as message\n")
                # print("response from llm parser function after n\n")
                await cl.Message(content=f"{response}",  author="System").send()
                msg = await cl.AskUserMessage(content="Anything more? or say bye to end",timeout=100000).send()
            print("\nbye\n")
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