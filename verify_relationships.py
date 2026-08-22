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

query = """
MATCH ()-[r:CONNECTED_TO]->()
RETURN count(r) AS relationship_count
"""

try:
    with driver.session() as session:
        result = session.run(query)
        record = result.single()

        print("CONNECTED_TO relationships:", record["relationship_count"])

finally:
    driver.close()