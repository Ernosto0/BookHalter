import re
from projects.management.commands import addbooks 
def extract_book_and_author(data):
    try: 
         # Split the input data by the known delimiters: period, newline, or numbers with periods
        # and ensure that the following character is an uppercase letter (start of a book title)
        pairs = re.split(r'\.\s*|\n|\d+\.\s*(?=[A-Z])', data)
        results = []
        for pair in pairs:
            # Ignore empty strings that may result from splitting
            if not pair.strip():
                continue
            # Split the pair by " by "
            if ' by ' in pair:
                book, author = pair.split(' by ')
                # Strip any remaining whitespace and period
                book = book.strip()
                author = author.strip().rstrip('.')
                results.append((book, author))
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
    return []

def ex(input_str):
    book_list = []
    for title, author in extract_book_and_author(input_str):
        book_list.append({'title': title, 'author': author})
    
    return book_list