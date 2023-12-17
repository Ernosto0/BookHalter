
import openai
import sqlite3
from aifolder import aimessage as aim
from aifolder import extract_book_data as ed
from projects.management.commands import addbooks
def gpt_main():

    openai.api_key = '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'
    while True:
        message = f"Make 2 book suggestions based on the parameters of the user: {aim.userdata}"

        if message:
            aim.aqmessages.append(
                {"role": "user", "content": message},
            )
            chat = openai.chat.completions.create(
                model="gpt-3.5-turbo", messages= aim.aqmessages
   
            )
        reply = chat.choices[0].message.content
        print(reply)
        recomended_books = ed.ex(reply)
        aim.aqmessages.append({"role": "assistant", "content": reply})
    
        addbooks.add_books(recomended_books)  
        print(recomended_books)
        return recomended_books
        
