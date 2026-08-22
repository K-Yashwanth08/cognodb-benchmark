import os
import time
import random

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, TransientError


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


# -----------------------------
# Driver
# -----------------------------

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD),
    connection_timeout=30,
    connection_acquisition_timeout=30,
    max_connection_lifetime=300
)


# -----------------------------
# Benchmark settings
# -----------------------------

WARMUP_RUNS = 5
BENCHMARK_RUNS = 30

TEST_USER_IDS = [
    0, 1, 2, 3, 4,
    10, 20, 30, 40, 50
]

MAX_RETRIES = 2


# -----------------------------
# Point Lookup
# -----------------------------

POINT_LOOKUP_QUERY = """
MATCH (u:User {id: $user_id})
RETURN u.id AS id
"""


def point_lookup(user_id):

    with driver.session() as session:

        start = time.perf_counter()

        result = session.run(
            POINT_LOOKUP_QUERY,
            user_id=user_id
        )

        record = result.single()

        end = time.perf_counter()

        latency_ms = (end - start) * 1000

        return latency_ms, record["id"]


# -----------------------------
# 1-Hop
# -----------------------------

ONE_HOP_QUERY = """
MATCH (u:User {id: $user_id})
      -[:CONNECTED_TO]->(neighbor)
RETURN count(neighbor) AS count
"""


def one_hop(user_id):

    with driver.session() as session:

        start = time.perf_counter()

        result = session.run(
            ONE_HOP_QUERY,
            user_id=user_id
        )

        record = result.single()

        end = time.perf_counter()

        latency_ms = (end - start) * 1000

        return latency_ms, record["count"]


# -----------------------------
# 2-Hop
# -----------------------------

TWO_HOP_QUERY = """
MATCH (u:User {id: $user_id})
      -[:CONNECTED_TO*2]->(neighbor)
RETURN count(DISTINCT neighbor) AS count
"""


def two_hop(user_id):

    with driver.session() as session:

        start = time.perf_counter()

        result = session.run(
            TWO_HOP_QUERY,
            user_id=user_id
        )

        record = result.single()

        end = time.perf_counter()

        latency_ms = (end - start) * 1000

        return latency_ms, record["count"]


# -----------------------------
# 3-Hop
# -----------------------------

THREE_HOP_QUERY = """
MATCH (u:User {id: $user_id})
      -[:CONNECTED_TO*3]->(neighbor)
RETURN count(DISTINCT neighbor) AS count
"""


def three_hop(user_id):

    for attempt in range(MAX_RETRIES + 1):

        try:

            with driver.session() as session:

                start = time.perf_counter()

                result = session.run(
                    THREE_HOP_QUERY,
                    user_id=user_id
                )

                record = result.single()

                end = time.perf_counter()

                latency_ms = (end - start) * 1000

                return latency_ms, record["count"]

        except (ServiceUnavailable, TransientError) as error:

            print(
                f"Connection error for User {user_id}. "
                f"Retry {attempt + 1}/{MAX_RETRIES}"
            )

            if attempt < MAX_RETRIES:

                time.sleep(2)

                global driver

                try:
                    driver.close()
                except Exception:
                    pass

                driver = GraphDatabase.driver(
                    URI,
                    auth=(USERNAME, PASSWORD),
                    connection_timeout=30,
                    connection_acquisition_timeout=30,
                    max_connection_lifetime=300
                )

            else:

                print(
                    f"3-hop failed for User {user_id}: "
                    f"{type(error).__name__}"
                )

                return None, None


# -----------------------------
# Percentile
# -----------------------------

def percentile(values, percentage):

    values = sorted(values)

    if not values:
        return None

    index = int((percentage / 100) * (len(values) - 1))

    return values[index]


# -----------------------------
# Point Lookup Benchmark
# -----------------------------

print("Starting point-lookup warm-up...")

for i in range(WARMUP_RUNS):

    user_id = random.choice(TEST_USER_IDS)

    latency, result_id = point_lookup(user_id)

    print(
        f"Warm-up {i + 1}: "
        f"User {result_id}, "
        f"{latency:.3f} ms"
    )


print()
print("Starting point-lookup benchmark...")
print()

point_latencies = []

for i in range(BENCHMARK_RUNS):

    user_id = random.choice(TEST_USER_IDS)

    latency, result_id = point_lookup(user_id)

    point_latencies.append(latency)

    print(
        f"Run {i + 1}: "
        f"User {result_id}, "
        f"{latency:.3f} ms"
    )


print()
print("==============================")
print("POINT LOOKUP RESULTS")
print("==============================")

print(f"Runs: {len(point_latencies)}")
print(f"Minimum: {min(point_latencies):.3f} ms")
print(f"Maximum: {max(point_latencies):.3f} ms")
print(f"P50: {percentile(point_latencies, 50):.3f} ms")
print(f"P95: {percentile(point_latencies, 95):.3f} ms")


# -----------------------------
# 1-Hop Benchmark
# -----------------------------

print()
print("Starting 1-hop benchmark...")
print()

one_hop_latencies = []

for i in range(BENCHMARK_RUNS):

    user_id = random.choice(TEST_USER_IDS)

    latency, count = one_hop(user_id)

    one_hop_latencies.append(latency)

    print(
        f"Run {i + 1}: "
        f"User {user_id}, "
        f"Neighbors {count}, "
        f"{latency:.3f} ms"
    )


print()
print("==============================")
print("1-HOP RESULTS")
print("==============================")

print(f"Runs: {len(one_hop_latencies)}")
print(f"Minimum: {min(one_hop_latencies):.3f} ms")
print(f"Maximum: {max(one_hop_latencies):.3f} ms")
print(f"P50: {percentile(one_hop_latencies, 50):.3f} ms")
print(f"P95: {percentile(one_hop_latencies, 95):.3f} ms")


# -----------------------------
# 2-Hop Benchmark
# -----------------------------

print()
print("Starting 2-hop benchmark...")
print()

two_hop_latencies = []

for i in range(BENCHMARK_RUNS):

    user_id = random.choice(TEST_USER_IDS)

    latency, count = two_hop(user_id)

    two_hop_latencies.append(latency)

    print(
        f"Run {i + 1}: "
        f"User {user_id}, "
        f"2-hop users {count}, "
        f"{latency:.3f} ms"
    )


print()
print("==============================")
print("2-HOP RESULTS")
print("==============================")

print(f"Runs: {len(two_hop_latencies)}")
print(f"Minimum: {min(two_hop_latencies):.3f} ms")
print(f"Maximum: {max(two_hop_latencies):.3f} ms")
print(f"P50: {percentile(two_hop_latencies, 50):.3f} ms")
print(f"P95: {percentile(two_hop_latencies, 95):.3f} ms")


# -----------------------------
# 3-Hop Benchmark
# -----------------------------

print()
print("Starting 3-hop benchmark...")
print()

three_hop_latencies = []
three_hop_failures = 0

for i in range(BENCHMARK_RUNS):

    user_id = random.choice(TEST_USER_IDS)

    latency, count = three_hop(user_id)

    if latency is None:

        three_hop_failures += 1

        print(
            f"Run {i + 1}: "
            f"User {user_id}, "
            f"FAILED"
        )

        continue

    three_hop_latencies.append(latency)

    print(
        f"Run {i + 1}: "
        f"User {user_id}, "
        f"3-hop users {count}, "
        f"{latency:.3f} ms"
    )


print()
print("==============================")
print("3-HOP RESULTS")
print("==============================")

print(f"Successful runs: {len(three_hop_latencies)}")
print(f"Failed runs: {three_hop_failures}")

if three_hop_latencies:

    print(
        f"Minimum: "
        f"{min(three_hop_latencies):.3f} ms"
    )

    print(
        f"Maximum: "
        f"{max(three_hop_latencies):.3f} ms"
    )

    print(
        f"P50: "
        f"{percentile(three_hop_latencies, 50):.3f} ms"
    )

    print(
        f"P95: "
        f"{percentile(three_hop_latencies, 95):.3f} ms"
    )


# -----------------------------
# Close driver
# -----------------------------

driver.close()

print()
print("Benchmark completed.")