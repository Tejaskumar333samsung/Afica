import pandas as pd
import sqlite3
import json
import re
from langchain_ollama import OllamaLLM
from datetime import datetime
DB_PATH = "./data/ads.db"
TABLE_NAME = "Structured_Ad_calendar"

# Setup local LLM using Ollama Mistral

llm = OllamaLLM(model="mistral")

def prompt_llm_for_all_rows(df_to_dict):
    print(f"\n **************************prompting LLM for entire CSV******************************** \n",)
    # raw_json = df.to_dict(orient="records")
    # print(f"\n **************************raw_json = to_dict******************************* \n",)
    # print(f"{df_to_dict}\n")

    # { row_dict.get("Ad Id")}
    prompt = f"""
    You are an intelligent assistant for data correction and structuring. You will be given a list of ad rows from a CSV file with some values missing or vague values.
    Your task is to:
    1. Fill each and every missing fields (e.g. end time, company name, placement on device) using natural language hints 
    in other columns of the row (like "plays for 30 minutes" or "noon") and make it machine(LLM) understandable.
    2. Standardize time fields to format: YYYY-MM-DD HH:MM:SS
    3. if no day mentioned assume today's date.
    4. Always output strict valid **JSON array** of rows each row having these exact keys:
    ["ad_id", "company_name", "location", "start_time", "end_time", "description", "placement", "rb_nrb", "availability"]
    Do not add explanations,do not add invalid escape characters, do not use any escape underscores(\_) also do not add any commentary only output with a pur JSON array.
    {json.dumps(df_to_dict, ensure_ascii=False)}
    Respond only with the corrected JSON object.
    for example if this is my calender AD104,"Pizza Hut",Kolkata,,,"Pizza Hut ad shall play for 1 hour from 2 pm",Top,NRb,Available with columns Ad Id,Company Name,Location,Start Time,End Time,Description,Placement on Device,Rb/NRb,Availability my output shall be like :
    [
  {{
    "ad_id": "AD104",
    "company_name": "Pizza Hut",
    "location": "Kolkata",
    "start_time": "2025-06-30 14:00:00",
    "end_time": "2025-06-30 15:00:00",
    "description": "Pizza Hut ad shall play for 1 hour from 2 pm",
    "placement": "Top",
    "rb_nrb": "NRb",
    "availability": "Available"
  }}
]	
    if today is 2025-06-30. 
	

    """
    print(f"\n **************************invoking prompt******************************* \n",)

    return llm.invoke(prompt)

def extract_json_from_response(response):
    try:
        print("\n **************************returning json response ******************************* \n")
        return json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                print("\n **************************returning json match group******************************* \n")
                return json.loads(match.group())
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON extraction failed: {e}")
        else:
            raise ValueError("No JSON object found in response.")
        
def normalize_time(tstr):
    try:
        # print("\n **************************normalizing time******************************* \n")
        return datetime.strptime(tstr.strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return tstr  # If already normalized or invalid, leave as it is
    
def create_table_if_not_exists(conn):
    cursor = conn.cursor()
    cursor.execute(f"""
        DROP TABLE IF EXISTS Structured_Ad_calendar;
    """)
    conn.commit()
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS Structured_Ad_calendar (
            ad_id TEXT PRIMARY KEY,
            company_name TEXT,
            location TEXT,
            start_time TEXT,
            end_time TEXT,
            description TEXT,
            placement TEXT,
            rb_nrb TEXT,
            availability TEXT
        )
    """)
    conn.commit()
    print("\n **********************dropping table if exist, create table if not exist done******************************* \n")
    
def process_csv_with_llm(df1):
    print("\n **************************processing csv with LLM******************************* \n")
    # df = pd.read_csv(csv_path)
    # df = df1.fillna(" ")
    # structured_rows = []
    llm_response = None
    try :
        llm_response = prompt_llm_for_all_rows(df1)
        structured_list = extract_json_from_response(llm_response)

        for corrected in structured_list:
            corrected["start_time"] = normalize_time(corrected.get("start_time", ""))
            corrected["end_time"] = normalize_time(corrected.get("end_time", ""))
            # structured_rows.append(corrected)
        
        with sqlite3.connect(DB_PATH) as conn:
            create_table_if_not_exists(conn)
            pd.DataFrame(structured_list).to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
            print("\n **************************data written into sqlDB ******************************* \n")
    except Exception as e:
            print(f"\nFailed to process full csv : {e}")
            print(f"\nRaw LLM response: {llm_response}")
    return
