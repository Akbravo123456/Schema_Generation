import streamlit as st
import requests
from records import view_records, save_records  # Import the records page function and save_records

BASE_URL = "http://127.0.0.1:8000"

if "current_page" not in st.session_state:
    st.session_state.current_page = "main"  

def switch_page(page: str):
    """Switch between pages."""
    st.session_state.current_page = page

def schema_generator():
    st.title("Schema Generator")
    st.header("Enter Prompt")
    prompt = st.text_area("Describe your database requirements:")

    st.header("Bulk Upload Prompts")
    uploaded_files = st.file_uploader(
        "Upload text, structured, semi-structured, or unstructured files",
        accept_multiple_files=True,
    )

    if st.button("Generate Schema"):
        if prompt or uploaded_files:
            payload = []

            if prompt.strip():
                payload.append({"filename": "single_prompt.txt", "content": prompt})

            if uploaded_files:
                for uploaded_file in uploaded_files:
                    content = uploaded_file.read().decode("utf-8")
                    payload.append({"filename": uploaded_file.name, "content": content})

            try:
                response = requests.post(f"{BASE_URL}/bulk-upload", json=payload)
                if response.status_code == 200:
                    results = response.json()
                    st.success("Schema generated successfully!")
                    for filename, schema in results.items():
                        st.subheader(f"Schema for {filename}")
                        st.json(schema)
                else:
                    st.error("Failed to generate schema.")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a prompt or upload files.")

    if st.button("Save Records"):
        try:
            save_records(payload) 
            st.success("Records saved successfully!")
        except Exception as e:
            st.error(f"Error saving records: {e}")

    if st.button("View Records"):
        switch_page("records")

if st.session_state.current_page == "main":
    schema_generator()
elif st.session_state.current_page == "records":
    view_records()
