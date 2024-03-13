import requests
import concurrent.futures


def search_book_by_title(title):
    search_url = "https://www.googleapis.com/books/v1/volumes"
    search_params = {'q': f'intitle:{title}', 'maxResults': 1, 'langRestrict': 'en', 'orderBy': 'newest'}

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
    search_params = {'title': title}
    response = requests.get(search_url, params=search_params)

    if response.status_code == 200:
        search_data = response.json()
        if search_data['numFound'] > 0:
            book = search_data['docs'][0]  # Take the first book from the search result
            id_amazon = book.get('id_amazon', ['N/A'])[0]  # Takes the first Amazon ID if available
            return {
                'id_amazon': id_amazon}
        else:
            return f"No results found for '{title}'."
    else:
        return "Failed to fetch data."


def main(titles):
    # Initialize dictionary for each book title
    book_data = {title[0]: {} for title in titles}  # Use the first element of each tuple (the title) as the key

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # Dispatch Google Books search tasks, using just the title for each task
        google_books_futures = {executor.submit(search_book_by_title, title[0]): title[0] for title in titles}

        for future in concurrent.futures.as_completed(google_books_futures):
            title = google_books_futures[future]  # This is now just the book title, not a tuple
            try:
                result = future.result()
                if isinstance(result, dict):
                    book_data[title].update(result)  # No error here since title is consistent with book_data keys
            except Exception as e:
                book_data[title]['error'] = str(e)  # Handle errors if needed

        # Dispatch Open Library Amazon ID search tasks, using just the title
        open_library_futures = {executor.submit(get_amazon_id_by_title, title[0]): title[0] for title in titles}

        for future in concurrent.futures.as_completed(open_library_futures):
            title = open_library_futures[future]  # Again, just the book title
            try:
                amazon_id = future.result()
                if amazon_id:
                    book_data[title]['id_amazon'] = amazon_id  # Consistent use of title as key
            except Exception as e:
                book_data[title]['error'] = str(e)  # Handle errors if needed

    return list(book_data.values())



