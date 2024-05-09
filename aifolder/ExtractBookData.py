import re

def extract_books_info(gpt_output):
    try:
        # Regular expression to match book titles, authors, and explanations
        pattern = r"(.+?) by (.+?): (.+?)(?=\.\n|$)"
        matches = re.findall(pattern, gpt_output)

        if not matches:
            raise ValueError("No book recommendations found in the GPT response.")

        # Extract book titles, authors, and explanations
        books_info = [{'title': match[0], 'author': match[1], 'explanation': match[2]} for match in matches]

        return books_info

    except Exception as e:
        # Log the error, return an error message, or take other appropriate action
        print(f"An error occurred: {e}")
        return []
    


