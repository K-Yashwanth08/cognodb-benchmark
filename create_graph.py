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
CREATE
    (a:Person {name: 'Alice', age: 25}),
    (b:Person {name: 'Bob', age: 30}),
    (c:Person {name: 'Charlie', age: 28}),
    (a)-[:FRIENDS_WITH]->(b),
    (b)-[:FRIENDS_WITH]->(c)
RETURN a, b, c
"""

try:
    with driver.session() as session:
        result = session.run(query)

        for record in result:
            print(record)

finally:
    driver.close()