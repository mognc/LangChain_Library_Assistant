from utils.fuzzy_matching import get_best_match
from app import extract_search_intent

def search_books(query, faiss_index, collection):

    refined_query, field = extract_search_intent(query)["value"], extract_search_intent(query)["field"]
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