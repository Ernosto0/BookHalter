from math import log
import mysql.connector
import logging
from fuzzywuzzy import fuzz
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check and delete duplicate books in the database'

    def handle(self, *args, **options):
        self.main()

    def check_duplicates(self):
        db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="myprojectdb"
        )

        cursor = db_connection.cursor()

        duplicate_query = """
        SELECT name, author, COUNT(*)
        FROM projects_books
        GROUP BY name, author
        HAVING COUNT(*) > 1;
        """

        cursor.execute(duplicate_query)
        duplicates = cursor.fetchall()

        if duplicates:
            logger.info("Duplicate audit completed. Duplicates found:")
            for duplicate in duplicates:
                print(f"name: {duplicate[0]}, Author: {duplicate[1]}, Count: {duplicate[2]}") # type: ignore
        else:
            logger.info("Duplicate audit completed. No duplicates found.")

        cursor.close()
        db_connection.close()

    def find_potential_duplicates(self, threshold=90):
        try:
            db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345",
                database="myprojectdb"
            )
            cursor = db_connection.cursor(dictionary=True)

            cursor.execute("SELECT id, name, author, created FROM projects_books")
            books = cursor.fetchall()
            
            potential_duplicates = []

            logger.info(f"Fetched {len(books)} books from the database.")
            
            for book in books:
                matches = []
                for other_book in books:
                    if book['id'] != other_book['id']: # type: ignore
                        title_similarity = max(fuzz.token_sort_ratio(book['name'], other_book['name']), fuzz.token_set_ratio(book['name'], other_book['name'])) # type: ignore
                        author_similarity = max(fuzz.token_sort_ratio(book['author'], other_book['author']), fuzz.token_set_ratio(book['author'], other_book['author'])) # type: ignore

                        if title_similarity > threshold and author_similarity > threshold:
                            matches.append(other_book)
                
                if matches:
                    logger.info(f"Found potential duplicates for book: {book['name']} by {book['author']}") # type: ignore
                    potential_duplicates.append((book, matches))

            cursor.close()
            db_connection.close()
            
            return potential_duplicates
        except Exception as e:
            logger.error(f"An error occurred when finding potential duplicates: {e}")
            return []

    def delete_duplicates(self):
        logger.info("Starting duplicate deletion process...")
        potential_duplicates = self.find_potential_duplicates(threshold=85)
        logger.info("Potential duplicates found:", potential_duplicates) 
        
        if potential_duplicates:
            logger.info("Duplicate audit completed. Duplicates found:")
            db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345",
                database="myprojectdb"
            )
            cursor = db_connection.cursor()

            # Track processed book IDs to avoid processing duplicates twice
            processed_ids = set()
            
            for book, duplicates in potential_duplicates:
                if book['id'] not in processed_ids:
                    try:
                        # Include the original book in the sorting process
                        all_books = [book] + duplicates
                        # Sort all related books by creation date
                        all_books_sorted = sorted(all_books, key=lambda x: x['created'])
                        # Keep the first created book and delete the rest
                        books_to_delete = all_books_sorted[1:]

                        for duplicate in books_to_delete:
                            cursor.execute("DELETE FROM projects_books WHERE id = %s", (duplicate['id'],))
                            db_connection.commit()
                            logger.info(f"Deleted duplicate book: {duplicate['name']} by {duplicate['author']}")
                            processed_ids.add(duplicate['id'])  # Mark this duplicate as processed
                        
                        processed_ids.add(book['id'])  # Mark the original book as processed
                    except mysql.connector.IntegrityError as e:
                        db_connection.rollback()
                        logger.error(f"IntegrityError when deleting '{duplicate['name']}': {e}")

            cursor.close()
            db_connection.close()
        else:
            logger.info("Duplicate audit completed. No duplicates found.")

    def main(self):
        while True:
            print("Select an option:")
            print("1. Check duplicates")
            print("2. Delete duplicates")
            print("3. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.check_duplicates()
            elif choice == "2":
                self.delete_duplicates()
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")
