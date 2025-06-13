import pandas as pd
import sqlite3
import json
import re
from langchain_ollama import OllamaLLM
from datetime import datetime
DB_PATH = "./ads.db"
TABLE_NAME = "Structured_Ad_calendar"

# Setup local LLM using Ollama Mistral

llm = OllamaLLM(model="mistral")

def prompt_llm_for_row(row_dict):
    print(f"\n **************************prompting LLM for row - { row_dict.get("Ad Id")}******************************* \n",)
    prompt = f"""
    You are an intelligent assistant for data correction and structuring. You will be given an ad row with missing or vague values.
    Your task is to:
    1. Fill any missing fields (e.g. end time, company name, placement on device) using natural language hints in other columns of the row (like "plays for 30 minutes" or "noon").
    2. Standardize time fields to format: YYYY-MM-DD HH:MM:SS
    3. Fix spelling or casing errors (e.g. rb can be mistakenly written as pb).
    4. Always output strict valid JSON, using only double quotes, no markdown, no commentary.
    Return a JSON with the following keys only:
    ["ad_id", "company_name", "location", "start_time", "end_time", "description", "placement", "rb_nrb", "availability"]
    Ad row:
    {json.dumps(row_dict, ensure_ascii=False)}
    Respond only with the corrected JSON object.
    """
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
        print("\n **************************normalizing time******************************* \n")
        return datetime.strptime(tstr.strip(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return tstr  # If already normalized or invalid, leave as it is
    
def create_table_if_not_exists(conn):
    cursor = conn.cursor()
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
    print("\n **************************create table if not exist done******************************* \n")
    
def process_csv_with_llm(csv_path):
    print("\n **************************processing csv with LLM******************************* \n")
    df = pd.read_csv(csv_path)
    df = df.fillna(" ")
    structured_rows = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        try:
            llm_response = prompt_llm_for_row(row_dict)
            corrected = extract_json_from_response(llm_response)
            corrected["start_time"] = normalize_time(corrected.get("start_time", ""))
            corrected["end_time"] = normalize_time(corrected.get("end_time", ""))
            structured_rows.append(corrected)
        except Exception as e:
            print(f"Failed to process row {row_dict.get('ad_id')}: {e}")
            print(f"Raw LLM response: {llm_response}")
    with sqlite3.connect(DB_PATH) as conn:
        create_table_if_not_exists(conn)
        pd.DataFrame(structured_rows).to_sql(TABLE_NAME, conn, if_exists="append", index=False,method="multi")
        print("\n **************************dataframe to sql done******************************* \n")
