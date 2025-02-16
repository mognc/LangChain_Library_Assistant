import pickle
from langchain.vectorstores import FAISS

def create_faiss_index(books_with_embeddings):
    text_embedding_pairs = []
    metadata_list = []

    for book in books_with_embeddings:
        if "title_embedding" in book:
            text_embedding_pairs.append((book["title"], book["title_embedding"]))
            metadata_list.append({"_id": str(book["_id"]), "field": "title"})

        if "author_embedding" in book:
            text_embedding_pairs.append((book["author"], book["author_embedding"]))
            metadata_list.append({"_id": str(book["_id"]), "field": "author"})

        if "category_embedding" in book:
            text_embedding_pairs.append((book["category"], book["category_embedding"]))
            metadata_list.append({"_id": str(book["_id"]), "field": "category"})

    
    if not text_embedding_pairs:
        raise ValueError("No valid text embeddings found for FAISS index.")

    faiss_index = FAISS.from_embeddings(text_embedding_pairs, embeddings)
    faiss_index.add_texts([pair[0] for pair in text_embedding_pairs], metadatas=metadata_list)

    faiss_index.save_local("faiss_index")
    with open("metadata.pkl", "wb") as f:
      pickle.dump(metadata_list, f)

    print("FAISS index created successfully!")
    return faiss_index

def load_faiss_index(embeddings):
    try:
        faiss_index = FAISS.load_local("data/Faiss_index", embeddings,allow_dangerous_deserialization=True)
        with open("data/metadata.pkl", "rb") as f:
            metadata_list = pickle.load(f)
        print("✅ FAISS index loaded successfully!")
        return faiss_index, metadata_list
    except Exception as e:
        print(f"⚠️ Failed to load FAISS index: {e}")
        return None, None