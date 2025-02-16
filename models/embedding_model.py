import os
from langchain.embeddings.openai import OpenAIEmbeddings


os.environ["OPENAI_API_KEY"] = "key"
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

def create_separate_embeddings(books):
    for book in books:
        if "title" in book:
            book["title_embedding"] = embeddings.embed_query(book["title"])
        if "author" in book:
            book["author_embedding"] = embeddings.embed_query(book["author"])
        if "category" in book:
            book["category_embedding"] = embeddings.embed_query(book["category"])
    return books

def update_books_with_embeddings(books_with_embeddings):
    for book in books_with_embeddings:
        if "_id" in book:
            collection.update_one(
                {"_id": book["_id"]}, 
                {"$set": {
                    "title_embedding": book.get("title_embedding"),
                    "author_embedding": book.get("author_embedding"),
                    "category_embedding": book.get("category_embedding")
                }}
            )
    print("Embeddings added to books in database!")