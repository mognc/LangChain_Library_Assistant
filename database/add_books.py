def add_books_to_db():
    books = [
        {"title": "Ali", "author": "Ahmad", "category": "LOL", "description": "Test"},
    ]
    collection.insert_many(books)
    print("Books added to database!")

add_books_to_db()