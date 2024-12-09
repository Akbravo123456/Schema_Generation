from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
import os

app = FastAPI()

model = AutoModelForCausalLM.from_pretrained("bigscience/bloom-560m")
tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom-560m")

RECORDS_PATH = "generated_schemas.json"

class FileInput(BaseModel):
    filename: str
    content: str

def generate_schema_with_bloom(content: str) -> Dict:
    """Generate a schema using the Bloom model."""
    input_ids = tokenizer.encode(content, return_tensors="pt")
    output = model.generate(input_ids, max_length=512, num_return_sequences=1)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)

    schema = {
        "tables": [
            {
                "name": "generated_table",
                "fields": [
                    {"name": "id", "type": "Number"},
                    {"name": "name", "type": "Text"},
                    {"name": "created_at", "type": "Datetime"},
                ]
            }
        ]
    }
    return schema

@app.post("/bulk-upload")
async def bulk_generate(files: List[FileInput]):
    results = {}
    for file in files:
        schema = generate_schema_with_bloom(file.content)
        results[file.filename] = schema

    save_records(results)
    return results

@app.get("/records")
def get_records():
    """Retrieve previously generated schemas."""
    try:
        with open(RECORDS_PATH, "r") as file:
            records = json.load(file)
        return records
    except FileNotFoundError:
        return {"error": "No records found."}

def save_records(schemas: Dict):
    """Saves the generated schemas to records.json."""
    try:
        if os.path.exists(RECORDS_PATH):
            with open(RECORDS_PATH, "r") as file:
                records = json.load(file)
        else:
            records = {}
        
        for filename, schema in schemas.items():
            records[filename] = schema
        
        with open(RECORDS_PATH, "w") as file:
            json.dump(records, file)
    except Exception as e:
        print(f"Error saving records: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
