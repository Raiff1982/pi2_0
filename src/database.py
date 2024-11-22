import sqlite3
import os
import logging
from termcolor import colored

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_database(db_path):
    """Connect to the SQLite database specified by db_path."""
    if not os.path.exists(db_path):
        logging.error(colored(f"Error: Database file '{db_path}' not found.", "red"))
        return None
    try:
        conn = sqlite3.connect(db_path)
        logging.info("Opened database successfully")
        return conn
    except sqlite3.OperationalError as e:
        logging.error(colored(f"Error: {e}", "red"))
        return None

def get_table_names(conn):
    """Retrieve the names of all tables in the database."""
    try:
        table_names = []
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in tables.fetchall():
            table_names.append(table[0])
        return table_names
    except sqlite3.OperationalError as e:
        logging.error(colored(f"Error retrieving table names: {e}", "red"))
        return []

def get_column_names(conn, table_name):
    """Retrieve the names of all columns in the specified table."""
    try:
        column_names = []
        columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
        for col in columns:
            column_names.append(col[1])
        return column_names
    except sqlite3.OperationalError as e:
        logging.error(colored(f"Error retrieving column names for table '{table_name}': {e}", "red"))
        return []

def get_database_info(conn):
    """Retrieve information about all tables and their columns in the database."""
    try:
        table_dicts = []
        for table_name in get_table_names(conn):
            columns_names = get_column_names(conn, table_name)
            table_dicts.append({"table_name": table_name, "column_names": columns_names})
        return table_dicts
    except sqlite3.OperationalError as e:
        logging.error(colored(f"Error retrieving database info: {e}", "red"))
        return []

def ask_database(conn, query):
    """Execute a query on the database and return the results."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except sqlite3.OperationalError as e:
        logging.error(colored(f"Error executing query '{query}': {e}", "red"))
        return []

if __name__ == "__main__":
    db_path = "data/Chinook.db"
    conn = connect_to_database(db_path)
    if conn:
        print("Tables in the database:")
        print(get_table_names(conn))
        print("Database info:")
        print(get_database_info(conn))
        query = "SELECT * FROM albums LIMIT 5;"
        print("Query results:")
        print(ask_database(conn, query))