from fuzzywuzzy import process

def get_best_match(search_term, field, collection):
    db_values = collection.distinct(field)
    best_match, score = process.extractOne(search_term, db_values)
    return best_match if score > 80 else search_term