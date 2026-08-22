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
MATCH (p:Person)
RETURN p.name AS name, p.age AS age
ORDER BY p.name
"""

try:
    with driver.session() as session:
        result = session.run(query)

        for record in result:
            print(f"Name: {record['name']}, Age: {record['age']}")

finally:
    driver.close()