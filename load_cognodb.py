import os
import csv
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

CSV_FILE = "git_web_ml/git_web_ml/musae_git_edges.csv"

BATCH_SIZE = 1000

query = """
UNWIND $edges AS edge
MATCH (source:User {id: edge.source})
MATCH (target:User {id: edge.target})
MERGE (source)-[:CONNECTED_TO]->(target)
"""

batch = []
total_edges = 0

try:
    with driver.session() as session:

        with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:

                source = int(row["id_1"])
                target = int(row["id_2"])

                batch.append({
                    "source": source,
                    "target": target
                })

                if len(batch) == BATCH_SIZE:

                    session.run(
                        query,
                        edges=batch
                    ).consume()

                    total_edges += len(batch)

                    print("Relationships loaded:", total_edges)

                    batch = []

            # Load remaining edges
            if batch:

                session.run(
                    query,
                    edges=batch
                ).consume()

                total_edges += len(batch)

                print("Relationships loaded:", total_edges)

    print("All relationships loaded successfully.")

finally:
    driver.close()