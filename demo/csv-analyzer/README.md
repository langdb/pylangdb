# CSV Analyzer with LangDB

Ask natural language questions about your large CSV data! This app uses [LangDB](https://langdb.dev) to take your questions and analyze the data behind the scenes.

## Features

- Upload any CSV file (like LinkedIn engagement data)
- Ask questions in plain English
- Get smart insights
- Powered by [LangDB](https://github.com/langdb/pylangdb)

## Setup Instructions

1. **Clone the repo**  
   ```bash
    git clone https://github.com/langdb/pylangdb.git
    cd demo/csv-analyzer
    ```

2. **Install dependencies**
    ```bash
     pip install -r requirements.txt
    ```

3. **Set your LangDB API key**
    - Create a `.env` file:
    ```bash
     LANGDB_API_KEY=langdb_XXXXXX
    ```

    - Never commit this file to Git. Add it in `.gitignore`

4. **Add your CSV file**

5. **Run the app**
    ```bash
     python app.py
    ```

