from projects.models import Books
from fuzzywuzzy import process
from django.db.models import Q

def find_best_fuzzy_match(title, author, candidates, threshold=80):
    # Combine title and author for more comprehensive matching
    query = f"{title} {author}"

    # Combine titles and authors of candidate books for comparison
    candidate_strings = [f"{book.name} {book.author}" for book in candidates]

    # Use fuzzy matching to find the best match
    best_match, score = process.extractOne(query, candidate_strings) #type: ignore

    # Check if the best match meets the threshold
    if score >= threshold:
        return candidates[candidate_strings.index(best_match)]
    else:
        return None

def search_books_in_database(books_to_search):
    found_books = []
    
    for book_to_search in books_to_search:
        # Fetch a set of potential matches based on title or author
        potential_matches = Books.objects.filter(
            Q(name__icontains=book_to_search['title']) | 
            Q(author__icontains=book_to_search['author'])
        )

        if potential_matches:
            # Apply fuzzy matching to find the best match among the potential matches
            book = find_best_fuzzy_match(book_to_search['title'], book_to_search['author'], potential_matches)

            if book:
                found_books.append(book)
                print(book_to_search['title'] + " is found with fuzzy matching")
            else:
                print("No fuzzy match found for: " + book_to_search['title'])
        else:
            print("No potential matches found for: " + book_to_search['title'])

    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    print(found_books)
    return found_books
