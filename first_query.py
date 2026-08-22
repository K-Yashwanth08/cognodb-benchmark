import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

query = "RETURN 'Hello from CognoDB!' AS message"

try:
    with driver.session() as session:
        result = session.run(query)
        record = result.single()

        print(record["message"])

finally:
    driver.close()