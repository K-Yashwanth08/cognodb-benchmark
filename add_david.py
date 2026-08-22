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
MATCH (c:Person {name: 'Charlie'})
CREATE (d:Person {name: 'David', age: 32})
CREATE (c)-[:FRIENDS_WITH]->(d)
RETURN d.name AS name, d.age AS age
"""

try:
    with driver.session() as session:
        result = session.run(query)

        for record in result:
            print(f"Created: {record['name']}, Age: {record['age']}")

finally:
    driver.close()