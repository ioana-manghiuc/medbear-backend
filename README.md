# medical-ai-back-end

This is the server side of a medical chatbot website. Front-end available [here](https://github.com/ioana-manghiuc/medical-ai-front-end).

Requirements:
- [Python](https://www.python.org/downloads/)

Installation steps:
1. Download ZIP.
2. Create an empty folder and unarchive the contents of the ZIP.
3. **Delete the _.venv_ folder if it exists**
4. Open the newly created folder (at step 2) and open it in a terminal.
5. **py -m venv .venv**
6. **.venv\Scripts\activate**
7. **pip install -r requirements.txt**

**.env.vault**:
1. **dotenv-vault open**
2. **npx dotenv-vault@latest pull**
3. **npx dotenv-vault@latest open**

Then run **py app.py** to start the server
