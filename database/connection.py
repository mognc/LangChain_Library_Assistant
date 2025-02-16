import pymongo
from dotenv import load_dotenv
import streamlit as st
import os
load_dotenv()

def get_database():
    mongo_uri = st.secrets["mongo"]["uri"]
    if not mongo_uri:
        raise ValueError("❌ MONGO_URI is not set. Please check your environment variables.")
    
    client = pymongo.MongoClient(mongo_uri)
    return client.Library

db = get_database()
collection = db.books

def test_connection():
    try:
        print("Connection successful! Databases:", db.list_collection_names())
    except Exception as e:
        print("Connection failed:", e)

test_connection()