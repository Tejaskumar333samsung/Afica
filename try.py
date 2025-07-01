import chainlit as cl
import pandas as pd
import json


@cl.on_chat_start
async def start():
    res = await cl.AskUserMessage(content="do you want to upload a new csv file ?(y/n)", timeout=50).send()
    if res :
        # print("got y/n res\n")
        if str(res["output"]) == "y":
            files = None
            while files is None:
                files = await cl.AskFileMessage(content="Please upload a csv file to begin!", accept=["csv"], timeout= 100).send()
                csv_file = files[0]
            df1 = pd.read_csv(csv_file.path)
            csv_data1 = df1.to_dict(orient='records')
            csv_content1 = json.dumps(csv_data1, ensure_ascii=False)

            print(f"""csv_content json: \n{csv_content1}\n""")
            # await cl.SendTextMessage(content=f"csv_content: \n{csv_content1}\n").send()
            print(f"""csv_data to_dict : \n{csv_data1}\n""")
            # await cl.SendTextMessage(content=f"csv_data: \n{csv_data1}\n").send()
            print(f"""csv_file path: \n{type(csv_file.path)}\n""")
            # await cl.SendTextMessage(content=f"""csv_file path: \n{str(csv_file.path)}\n""").send()
            print(f"""csv_file name: \n{csv_file.name}\n""")
            # await cl.SendTextMessage(content=f"csv_file name: \n{csv_file.name}\n").send()
            print(f"""csv_file size: \n{csv_file.size}\n""")
            # await cl.SendTextMessage(content=f"csv_file size: \n{csv_file.size}\n").send()
            print(f"""df1: \n{df1["Start Time"]}\n""")
            # await cl.SendTextMessage(content=f"df1: \n{df1}\n").send()
