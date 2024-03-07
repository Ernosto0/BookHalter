import re


def extract_book_and_author(data):
    gpt_output = data

    try:
        # Regular expression to match book titles and authors
        book_pattern = r"\d+\.\s+(.+?)\s+by\s+(.+?)\."
        matches = re.findall(book_pattern, gpt_output)

        if not matches:
            raise ValueError("No book recommendations found in the GPT response.")

        books_and_authors = [(match[0], match[1]) for match in matches]

        # Extract greeting message
        greeting_end_index = gpt_output.find("1.")
        if greeting_end_index == -1:
            raise ValueError("Greeting message not found in the GPT response.")
        greeting_message = gpt_output[:greeting_end_index].strip()

        # Extract text after the last recommendation
        if matches:
            last_book_start_pos = gpt_output.rfind(f"{matches[-1][0]} by {matches[-1][1]}")
            last_book_end_pos = last_book_start_pos + len(f"{matches[-1][0]} by {matches[-1][1]}.")
            text_after_recommendations = gpt_output[last_book_end_pos:].strip()
        else:
            text_after_recommendations = ""

        return [books_and_authors, greeting_message, text_after_recommendations]

    except Exception as e:
        # Log the error, return an error message, or take other appropriate action
        print(f"An error occurred: {e}")
        return [], "An error occurred while processing the GPT response.", ""
