import os
import time
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

BATCH_SIZE = 1000
TOTAL_WRITES = 5000

create_query = """
UNWIND $rows AS row
CREATE (a:BenchmarkUser {id: row.id})
"""

try:
    with driver.session() as session:

        rows = []

        start = time.perf_counter()

        for i in range(TOTAL_WRITES):

            rows.append({
                "id": i
            })

            if len(rows) == BATCH_SIZE:

                session.run(
                    create_query,
                    rows=rows
                ).consume()

                rows = []

        if rows:
            session.run(
                create_query,
                rows=rows
            ).consume()

        end = time.perf_counter()

        elapsed = end - start
        writes_per_second = TOTAL_WRITES / elapsed

        print("Write Throughput")
        print("----------------")
        print("Nodes written:", TOTAL_WRITES)
        print(f"Time: {elapsed:.3f} seconds")
        print(f"Throughput: {writes_per_second:.2f} writes/second")

finally:
    driver.close()