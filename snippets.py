import logging
import argparse
import psycopg2

# Set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established.")


def put(name, snippet, hide):
    """Store a snippet with an associated name."""
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
        
    try:
        with connection, connection.cursor() as cursor:
            cursor.execute("insert into snippets values (%s, %s, %s)", (name,snippet, hide))
   
    except psycopg2.IntegrityError:
        with connection, connection.cursor() as cursor:
            cursor.execute("update snippets set message=%s, hide=%s where keyword=%s", (snippet, hide, name))
            
    logging.debug("Snippet stored successfully.")
    return name, snippet
    
def get(name):
    """Retrieve the snippet with a given name.
    If there is no such snippet, return '404: Snippet Not Found'.
    Returns the snippet.
    """
    with connection, connection.cursor() as cursor:
        cursor.execute("select message from snippets where keyword=%s", (name,))
        row = cursor.fetchone()
    
    if not row:
    # No snippet was found with that name.
        logging.info(str(name) + " not found in snippets database.")
        logging.debug("404 message returned.")
        return "404: Snippet Not Found"
    
    logging.info("Returning snippet {!r}: {!r}".format(name, row[0]))
    logging.debug("Snippet retrieved successfully.")
    return row[0]
    
def catalog():
    """Retrieve a list of all the keywords."""
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword from snippets where not hidden order by keyword")
        keywords = cursor.fetchall()
    logging.info("Returning all keywords")
    return keywords
    
def search(searchterm):
    """Return snippets with the search term in its messages."""
    searchterm = '%' + searchterm + '%'
    with connection, connection.cursor() as cursor:
        cursor.execute("select * from snippets where message like %s and not hidden", (searchterm,))
        rows = cursor.fetchall()
    logging.info("Returning snippet(s) with search term")
    logging.debug("Snippet(s) retrieved successfully.")
    return rows

def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")

# study this line and the one above
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

 # Subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    
# add hide optional argument
    put_parser.add_argument("--hide", help="hide the snippet", action="store_true")

 # Subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="Name of the snippet")
    
# Subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    catalog_parser = subparsers.add_parser("catalog", help="Return a catalog of all keywords")
    
# Subparser for the search command
    logging.debug("Constructing search subparser")
    search_parser = subparsers.add_parser("search", help="Search and return snippets")
    search_parser.add_argument("searchterm", help="Search terms to search snippets for")

    arguments = parser.parse_args()
    # Convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")

    if command == "put":
        #name and snippet on left hand side only being used to print
        name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    elif command == "catalog":
        keywords = catalog(**arguments)
        for keyword in keywords:
            print(keyword[0])
    elif command == "search":
        searchresults = search(**arguments)
        for searchresult in searchresults:
            print(searchresult[0] + " : " + searchresult[1])
        
if __name__ == "__main__":
    main()