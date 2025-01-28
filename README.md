# medical-ai-back-end

This is the server side of a medical chatbot website, implemented using the Flask framework.\
The data received is handled using three layers:
1. all operations and business logic are implemented in the **Logic layer**, with specific classes for the user and the chat
2. the business logic classes use the **Database layer** which contains DAO classes for the user and chat to retrieve information from the database (MongoDB)
3. the models used by the DAO objects are in the **Model layer**

Unit tests are written in the Tests folder.

!! Front-end available [here](https://github.com/ioana-manghiuc/medical-ai-front-end).

Requirements:
- [Python](https://www.python.org/downloads/)

Installation steps:
1. Download ZIP.
2. Create an empty folder and unarchive the contents of the ZIP.
3. Open the newly created folder in a terminal.
4. **py -m venv .venv**
5. **.venv\Scripts\activate**
6. **pip install -r requirements.txt**

**.env.vault** setup, which used to store environment variables securely:
1. **dotenv-vault open**
2. **npx dotenv-vault@latest pull**
3. **npx dotenv-vault@latest open**

Then run **py app.py** to start the server
