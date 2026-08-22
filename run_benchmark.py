import os
import time
import random
import csv

from dotenv import load_dotenv
from neo4j import GraphDatabase
from neo4j.exceptions import (
    ServiceUnavailable,
    TransientError,
    SessionExpired
)


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

if not URI or not USERNAME or not PASSWORD:
    raise ValueError(
        "Missing CognoDB credentials. "
        "Check COGNODB_URI, COGNODB_USERNAME, "
        "and COGNODB_PASSWORD."
    )


# ============================================================
# DRIVER
# ============================================================

def create_driver():

    return GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD),
        connection_timeout=30,
        connection_acquisition_timeout=30,
        max_connection_lifetime=120,
        max_connection_pool_size=5
    )


driver = create_driver()


# ============================================================
# BENCHMARK SETTINGS
# ============================================================

WARMUP_RUNS = 5
BENCHMARK_RUNS = 10
MAX_RETRIES = 2

# Delay for Point Lookup, 1-Hop and 2-Hop
RUN_DELAY = 1

# Extra delay for heavy 3-Hop queries
THREE_HOP_DELAY = 10


TEST_USER_IDS = [
    0, 1, 2, 3, 4,
    10, 20, 30, 40, 50
]


# ============================================================
# CSV SETTINGS
# ============================================================

CSV_FILE = "benchmark_results.csv"

csv_rows = []


# ============================================================
# REBUILD DRIVER
# ============================================================

def rebuild_driver():

    global driver

    try:
        driver.close()
    except Exception:
        pass

    print("Waiting before reconnecting to CognoDB...")

    time.sleep(10)

    for reconnect_attempt in range(5):

        try:

            print(
                f"Reconnecting to CognoDB... "
                f"Attempt {reconnect_attempt + 1}/5"
            )

            driver = create_driver()

            driver.verify_connectivity()

            print("CognoDB connection restored.")

            return True

        except Exception as error:

            print(
                f"Reconnect failed: "
                f"{type(error).__name__}"
            )

            try:
                driver.close()
            except Exception:
                pass

            time.sleep(10)

    print(
        "CognoDB is still unavailable "
        "after multiple reconnect attempts."
    )

    return False


# ============================================================
# EXECUTE QUERY WITH RETRY
# ============================================================

def execute_query(query, user_id):

    total_attempts = MAX_RETRIES + 1

    for attempt in range(total_attempts):

        try:

            with driver.session() as session:

                start = time.perf_counter()

                result = session.run(
                    query,
                    user_id=user_id
                )

                record = result.single()

                end = time.perf_counter()

                latency_ms = (
                    end - start
                ) * 1000

                if record is None:

                    print(
                        f"No result found for "
                        f"User {user_id}"
                    )

                    return None, None

                return latency_ms, record


        except (
            ServiceUnavailable,
            TransientError,
            SessionExpired
        ) as error:

            attempt_number = attempt + 1

            print(
                f"Connection error for User {user_id}: "
                f"{type(error).__name__}"
            )

            if attempt_number < total_attempts:

                print(
                    f"Retry "
                    f"{attempt_number}/{MAX_RETRIES}"
                )

                connection_restored = rebuild_driver()

                if not connection_restored:

                    print(
                        f"Unable to restore connection "
                        f"for User {user_id}."
                    )

                    return None, None

                print(
                    "Waiting 5 seconds before "
                    "retrying the query..."
                )

                time.sleep(5)

            else:

                print(
                    f"Query failed for User {user_id} "
                    f"after {total_attempts} attempts: "
                    f"{type(error).__name__}"
                )

                return None, None


        except Exception as error:

            print(
                f"Unexpected error for User "
                f"{user_id}: "
                f"{type(error).__name__} - {error}"
            )

            return None, None


# ============================================================
# QUERIES
# ============================================================

POINT_LOOKUP_QUERY = """
MATCH (u:User {id: $user_id})
RETURN u.id AS id
"""


ONE_HOP_QUERY = """
MATCH (u:User {id: $user_id})
      -[:CONNECTED_TO]->(neighbor)
RETURN count(neighbor) AS count
"""


TWO_HOP_QUERY = """
MATCH (u:User {id: $user_id})
      -[:CONNECTED_TO*2]->(neighbor)
WITH DISTINCT neighbor
RETURN count(neighbor) AS count
"""


# EXACTLY 3-HOP QUERY
THREE_HOP_QUERY = """
MATCH (u:User {id: $user_id})
      -[:CONNECTED_TO*3]->(neighbor)
WITH DISTINCT neighbor
RETURN count(neighbor) AS count
"""


# ============================================================
# BENCHMARK FUNCTIONS
# ============================================================

def point_lookup(user_id):

    latency, record = execute_query(
        POINT_LOOKUP_QUERY,
        user_id
    )

    if record is None:
        return None, None

    return latency, record["id"]


def one_hop(user_id):

    latency, record = execute_query(
        ONE_HOP_QUERY,
        user_id
    )

    if record is None:
        return None, None

    return latency, record["count"]


def two_hop(user_id):

    latency, record = execute_query(
        TWO_HOP_QUERY,
        user_id
    )

    if record is None:
        return None, None

    return latency, record["count"]


def three_hop(user_id):

    latency, record = execute_query(
        THREE_HOP_QUERY,
        user_id
    )

    if record is None:
        return None, None

    return latency, record["count"]


# ============================================================
# PERCENTILE
# ============================================================

def percentile(values, percentage):

    if not values:
        return None

    sorted_values = sorted(values)

    index = int(
        (percentage / 100)
        * (len(sorted_values) - 1)
    )

    return sorted_values[index]


# ============================================================
# SAVE CSV
# ============================================================

def save_csv():

    with open(
        CSV_FILE,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "Benchmark Type",
            "Run Number",
            "User ID",
            "Result Count",
            "Latency (ms)",
            "Status"
        ])

        writer.writerows(csv_rows)

    print()
    print(
        f"CSV file created successfully: "
        f"{CSV_FILE}"
    )


# ============================================================
# WARM-UP
# ============================================================

def run_warmup():

    print("Starting point-lookup warm-up...")

    for i in range(WARMUP_RUNS):

        user_id = random.choice(TEST_USER_IDS)

        latency, result_id = point_lookup(user_id)

        if latency is not None:

            print(
                f"Warm-up {i + 1}: "
                f"User {result_id}, "
                f"{latency:.3f} ms"
            )

        else:

            print(
                f"Warm-up {i + 1}: "
                f"User {user_id}, FAILED"
            )

        time.sleep(1)


# ============================================================
# GENERIC BENCHMARK
# ============================================================

def run_benchmark(
    benchmark_name,
    benchmark_function,
    result_label,
    delay
):

    print()
    print(
        f"Starting {benchmark_name} benchmark..."
    )
    print()

    latencies = []
    failures = 0

    for i in range(BENCHMARK_RUNS):

        user_id = random.choice(TEST_USER_IDS)

        run_number = i + 1

        latency, result = benchmark_function(
            user_id
        )


        # ========================================================
        # FAILED RUN
        # ========================================================

        if latency is None:

            failures += 1

            csv_rows.append([
                benchmark_name,
                run_number,
                user_id,
                "",
                "",
                "FAILED"
            ])

            print(
                f"Run {run_number}: "
                f"User {user_id}, FAILED"
            )


        # ========================================================
        # SUCCESSFUL RUN
        # ========================================================

        else:

            latencies.append(latency)

            if benchmark_name == "Point Lookup":
                csv_result = ""
            else:
                csv_result = result

            csv_rows.append([
                benchmark_name,
                run_number,
                user_id,
                csv_result,
                round(latency, 3),
                "SUCCESS"
            ])

            if benchmark_name == "Point Lookup":

                print(
                    f"Run {run_number}: "
                    f"User {result}, "
                    f"{latency:.3f} ms"
                )

            else:

                print(
                    f"Run {run_number}: "
                    f"User {user_id}, "
                    f"{result_label} {result}, "
                    f"{latency:.3f} ms"
                )


        # ========================================================
        # WAIT BEFORE NEXT RUN
        # ========================================================

        if run_number < BENCHMARK_RUNS:

            print(
                f"Waiting {delay} seconds "
                f"before next run..."
            )

            time.sleep(delay)


    # ============================================================
    # RESULTS
    # ============================================================

    print()
    print("==============================")
    print(
        f"{benchmark_name.upper()} RESULTS"
    )
    print("==============================")

    print(
        f"Successful runs: {len(latencies)}"
    )

    print(
        f"Failed runs: {failures}"
    )

    if latencies:

        print(
            f"Minimum: "
            f"{min(latencies):.3f} ms"
        )

        print(
            f"Maximum: "
            f"{max(latencies):.3f} ms"
        )

        print(
            f"P50: "
            f"{percentile(latencies, 50):.3f} ms"
        )

        print(
            f"P95: "
            f"{percentile(latencies, 95):.3f} ms"
        )

    else:

        print(
            "No successful benchmark runs."
        )

    return latencies


# ============================================================
# MAIN
# ============================================================

def main():

    try:

        # --------------------------------------------------------
        # VERIFY CONNECTION
        # --------------------------------------------------------

        print(
            "Checking CognoDB connection..."
        )

        driver.verify_connectivity()

        print(
            "Connected to CognoDB successfully."
        )

        print()


        # --------------------------------------------------------
        # WARM-UP
        # --------------------------------------------------------

        run_warmup()


        # --------------------------------------------------------
        # POINT LOOKUP
        # --------------------------------------------------------

        run_benchmark(
            "Point Lookup",
            point_lookup,
            "",
            RUN_DELAY
        )


        # --------------------------------------------------------
        # 1-HOP
        # --------------------------------------------------------

        run_benchmark(
            "1-Hop",
            one_hop,
            "Neighbors",
            RUN_DELAY
        )


        # --------------------------------------------------------
        # 2-HOP
        # --------------------------------------------------------

        run_benchmark(
            "2-Hop",
            two_hop,
            "2-hop users",
            RUN_DELAY
        )


        # --------------------------------------------------------
        # 3-HOP
        # --------------------------------------------------------

        run_benchmark(
            "3-Hop",
            three_hop,
            "3-hop users",
            THREE_HOP_DELAY
        )


        # --------------------------------------------------------
        # SAVE CSV
        # --------------------------------------------------------

        save_csv()

        print()
        print("Benchmark completed.")


    finally:

        try:

            driver.close()

            print(
                "CognoDB connection closed."
            )

        except Exception:
            pass


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()