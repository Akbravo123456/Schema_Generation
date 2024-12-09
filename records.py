import streamlit as st
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def view_records():
    try:
        response = requests.get(f"{BASE_URL}/records")
        response.raise_for_status()
        records = response.json()
        if records:
            for filename, schema in records.items():
                st.subheader(filename)
                st.json(schema)
        else:
            st.warning("No records found.")
    except requests.RequestException as e:
        st.error(f"Failed to fetch records: {e}")

def save_records(schemas):
    """Saves the generated schemas to records."""
    try:
        with open("generated_schemas.json", "r") as file:
            records = json.load(file)
    except FileNotFoundError:
        records = {}

    for schema in schemas:
        records[schema["filename"]] = schema["content"]

    with open("generated_schemas.json", "w") as file:
        json.dump(records, file)

if __name__ == "__main__":
    view_records()
