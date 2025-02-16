import streamlit as st
import json
import os
import pickle
from database.connection import get_database, test_connection
from models.faiss_index import load_faiss_index
from utils.fuzzy_matching import get_best_match
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

openai_api_key = st.secrets["OPENAI_API_KEY"]

if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY is not set. Please check your environment variables.")

# Use the key in your code
os.environ["OPENAI_API_KEY"] = openai_api_key


db = get_database()
collection = db.books
test_connection()

embeddings = OpenAIEmbeddings(
    model="text-embedding-ada-002"
)


faiss_index, metadata_list = load_faiss_index(embeddings)


llm = ChatOpenAI(model="gpt-4", temperature=0)
query_prompt = PromptTemplate(
    input_variables=["query"],
     template="""
    You are a smart assistant that corrects misspellings and extracts structured search queries.
    Convert the following user query into JSON format specifying "field" (title, author, category) and "value".

    If any word is misspelled, correct it before structuring the query.

    Example:

    User Query: "Show me books by J.K. Rowlng"
    Output: {{"field": "author", "value": "J.K. Rowling"}}

    User Query: "Find me books in the fatasy category"
    Output: {{"field": "category", "value": "Fantasy"}}

    User Query: "Show me books titled Harry Poter"
    Output: {{"field": "title", "value": "Harry Potter"}}

    Now process this query:
    User Query: "{query}"
    Output:
    """
)
llm_chain = LLMChain(llm=llm, prompt=query_prompt)

def extract_search_intent(query: str):
    response = llm_chain.invoke({"query": query})["text"].strip()
    try:
        parsed_response = json.loads(response)
        return parsed_response["value"], parsed_response["field"]
    except json.JSONDecodeError:
        print("⚠️ Failed to parse LLM response. Defaulting to title search.")
        return query, "title"

def search_books(query, faiss_index, collection):

    refined_query, field = extract_search_intent(query)
    corrected_query = get_best_match(refined_query, field, collection)
    keyword_results = list(collection.find({field: {"$regex": corrected_query, "$options": "i"}}))
    vector_results = faiss_index.similarity_search(corrected_query, k=3)
    
    faiss_results = []
    for v in vector_results:
        if v.page_content.lower() != corrected_query.lower():  # Prevents duplicate keyword matches
            faiss_results.append({"title": v.page_content})

    # Combine results
    combined_results = keyword_results + faiss_results

    return combined_results


# Streamlit UI
st.title("📚 Library Assistant Chatbot")

# Display Books
st.subheader("Available Books in Database")
books = list(collection.find({}, {"_id": 0, "title": 1, "author": 1, "category": 1}))
for book in books:
    st.write(f"📖 **{book['title']}** by {book['author']} (Category: {book['category']})")


# Search Bar
query = st.text_input("🔍 Search for a book, author, or category")

if query:
    search_results = search_books(query, faiss_index,collection)
    
    if search_results:
        st.subheader("Search Results")
        for result in search_results:
            st.write(f"📖 **Title:** {result.get('title', 'N/A')}")
            st.write(f"✍️ **Author:** {result.get('author', 'N/A')}")
            st.write(f"📂 **Category:** {result.get('category', 'N/A')}")
            st.write("---")
    else:
        st.warning("No matching books found.")