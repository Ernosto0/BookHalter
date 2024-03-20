import requests
import concurrent.futures
from fuzzywuzzy import fuzz

def search_book_by_title_and_author(title, author):
    search_url = "https://www.googleapis.com/books/v1/volumes"
    search_params = {'q': f'intitle:{title}+inauthor:{author}', 'maxResults': 1, 'langRestrict': 'en'}

    response = requests.get(search_url, params=search_params)

    if response.status_code == 200:
        search_data = response.json()
        books = search_data.get('items', [])

        if books:
            book = books[0]
            volume_info = book['volumeInfo']
            title = volume_info.get('title')
            author = volume_info.get('authors')
            year = volume_info.get('publishedDate', '').split('-')[0]  # Get only the year part
            description = volume_info.get('description', 'No description available.')
            cover_image = volume_info.get('imageLinks', {}).get('thumbnail', 'No cover image available.')
            id_amazon = get_amazon_id_by_title(title)
            return {
                'title': title,
                'author': author,
                'year': year,
                'description': description,
                'cover_image': cover_image
            }
        else:
            return f"No results found for '{title}'."
    else:
        return "Failed to fetch data."


# Example usage, replace 'your_api_key_here' with your actual Google Books API key


def get_amazon_id_by_title(title):
    search_url = "https://openlibrary.org/search.json"
    search_params = {'title': title, }
    response = requests.get(search_url, params=search_params)

    if response.status_code == 200:
        search_data = response.json()
        if search_data['numFound'] > 0:
            book = search_data['docs'][0]  # Take the first book from the search result
            id_amazon = book.get('id_amazon', ['N/A'])[0]  # Takes the first Amazon ID if available
            return {
                'id_amazon': id_amazon}
        else:
            return {}
    else:
        return {}


def is_match(fetched, expected, threshold=90):
    # Perform fuzzy matching for title and author
    title_score = fuzz.ratio(fetched.get('title', '').lower(), expected[0].lower())
    author_score = fuzz.ratio(fetched.get('author', '').lower(), expected[1].lower())

    # Check if both title and author match exceed the threshold
    return title_score >= threshold and author_score >= threshold

def main(titles):
    
    book_data = {}

    titles_with_authors = [(book['title'], book['author']) for book in titles]

    titles_for_openlibrary = {book['title']: {} for book in titles}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Dispatch Google Books search tasks, using just the title for each task
        google_books_futures = {executor.submit(search_book_by_title_and_author, title, author): (title, author) for
                                  title, author in titles_with_authors}

        for future in concurrent.futures.as_completed(google_books_futures):
            expected_title_author = google_books_futures[future]  # This is now just the book title, not a tuple
            try:
                fetched_book = future.result()
                if fetched_book:
                    book_data[expected_title_author] = fetched_book
                else:
                    book_data[expected_title_author] = {'error': 'No accurate match found'}
            except Exception as e:
                book_data[expected_title_author] = {'error': str(e)}

        # Dispatch Open Library Amazon ID search tasks, using just the title
        open_library_futures = {executor.submit(get_amazon_id_by_title, title): title for title in titles_for_openlibrary.keys()}

        for future in concurrent.futures.as_completed(open_library_futures):
            title = open_library_futures[future]  # The book title
            try:
                amazon_id_result = future.result()
                if amazon_id_result:
                    # Check if the book already has an entry in book_data
                    # Find the entry by matching the title
                    matching_entry = next((k for k in book_data.keys() if k[0] == title), None)
                    if matching_entry:
                        # Update the existing entry with the Amazon ID
                        book_data[matching_entry]['id_amazon'] = amazon_id_result['id_amazon']
                    else:
                        # Handle the case where the book wasn't found via Google Books API but has an Amazon ID
                        book_data[(title, '')] = {'id_amazon': amazon_id_result['id_amazon']}
            except Exception as e:
                if (title, '') not in book_data:
                    book_data[(title, '')] = {'error': str(e)}
                else:
                    # Update the error message if the title already exists in the book_data
                    book_data[(title, '')]['error'] = str(e)
    print(book_data)
    return list(book_data.values())



