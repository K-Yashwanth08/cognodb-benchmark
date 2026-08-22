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
MATCH (u:BenchmarkUser)
DETACH DELETE u
"""

try:
    with driver.session() as session:
        result = session.run(query)
        summary = result.consume()

        print("Benchmark data cleaned.")
        print("Nodes deleted:", summary.counters.nodes_deleted)

finally:
    driver.close()