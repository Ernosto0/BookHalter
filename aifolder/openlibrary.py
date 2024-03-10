import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import backoff
import ratelimit
from ratelimit import limits, sleep_and_retry



FIFTEEN_MINUTES = 900

@sleep_and_retry
@limits(calls=100, period=FIFTEEN_MINUTES)
@backoff.on_exception(backoff.expo, ratelimit.RateLimitException, max_time=60)
def search_book_by_title(title):
    search_url = "https://openlibrary.org/search.json"
    search_params = {'title': title}
    response = requests.get(search_url, params=search_params)

    if response.status_code == 200:
        search_data = response.json()
        if search_data['numFound'] > 0:
            book = search_data['docs'][0]  # Take the first book from the search result
            book_data = {
                'name': book.get('title', 'N/A'),
                'author': ', '.join(book.get('author_name', ['N/A'])),
                'published_year': book.get('first_publish_year', 'N/A'),
                'description': 'N/A',  # Default value if not found
                'featured_image_url': 'N/A'  # Default value if not found
            }

            cover_id = book.get('cover_i')
            if cover_id:
                book_data['featured_image_url'] = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

            ol_id = book.get('key', '').split('/')[-1]
            if ol_id:
                details_url = f"https://openlibrary.org/books/{ol_id}.json"
                details_response = requests.get(details_url)
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    description = details_data.get('description', {})
                    if isinstance(description, dict):
                        book_data['description'] = description.get('value', 'No description available.')
                    elif isinstance(description, str):
                        book_data['description'] = description
            return book_data
        else:
            return {'error': f"No results found for '{title}'."}
    else:
        return {'error': "Failed to fetch data."}

def main(book_titles):
    all_books_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Create a future for each book title
        future_to_title = {executor.submit(search_book_by_title, title): title for title in book_titles}
        
        # Process the futures as they complete
        for future in as_completed(future_to_title):
            book_data = future.result()

            # Check if book_data is a dictionary and does not contain 'error'
            if isinstance(book_data, dict) and 'error' not in book_data:
                all_books_data.append(book_data)

    return all_books_data


