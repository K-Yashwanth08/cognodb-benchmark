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
MATCH (a:Person {name: 'Alice'})
      -[:FRIENDS_WITH*3]->(person)
RETURN person.name AS name
"""

try:
    with driver.session() as session:
        result = session.run(query)

        for record in result:
            print("3-hop friend:", record["name"])

finally:
    driver.close()