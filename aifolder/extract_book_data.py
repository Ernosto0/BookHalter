import re

def extract_book_and_author(data):
    try: 
        pairs = re.split(r'\. (?=[A-Z])', data)
        results = []
        for pair in pairs:
            # Check if the book name is in quotes
            if '"' in pair:
                # Split the pair by the closing quote and " by "
                book, author = pair.split('" by ')
                # Remove the opening quote from the book name
                book = book.replace('"', '')
            else:
                # Split the pair by " by " for unquoted book names
                book, author = pair.split(' by ')
            # Strip any remaining whitespace and period
            book = book.strip()
            author = author.strip().rstrip('.')
            results.append((book, author))
        return results
    except:
        print("error")
    return []

def ex(input_str):
    book_list = []
    for title, author in extract_book_and_author(input_str):
        book_list.append({'title': title, 'author': author})
    return book_list