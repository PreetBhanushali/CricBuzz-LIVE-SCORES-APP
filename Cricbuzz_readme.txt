Cricket Analytics Dashboard

This project is a comprehensive cricket analytics dashboard built with Python, Streamlit, and a SQLite database. It provides real-time live match scores and a platform to manage and analyze player statistics.
Project Structurea

    app.py: The main application file that serves as the entry point for the Streamlit app. It handles page navigation.

    requirements.txt: Lists all the Python packages required to run the application.

    pages/: Contains the different pages of the application.

        live_matches.py: Displays the live cricket scorecard by fetching data from the Cricbuzz API.

        crud_operations.py: Provides a user interface for performing CRUD (Create, Read, Update, Delete) operations on player statistics.

    utils/: Contains utility files.

        db_connection.py: Handles the SQLite database connection and table initialization.

    sql_queries.py: A file to store all the SQL queries used in the application.

Setup Instructions

    Install Required Packages:

    pip install -r requirements.txt


    Add Your API Key:
    Open the pages/live_matches.py file and replace "YOUR_RAPIDAPI_KEY_HERE" with your personal API key from RapidAPI.

    Run the Application:

    streamlit run app.py


    Access the Dashboard:
    Your dashboard will open in your web browser, typically at http://localhost:8501.