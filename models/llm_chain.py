import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

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