import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# LOAD BENCHMARK RESULTS
# ============================================================

CSV_FILE = "benchmark_results.csv"

df = pd.read_csv(CSV_FILE)

print()
print("============================================================")
print("COGNODB BENCHMARK DATA")
print("============================================================")
print()

print(df)


# ============================================================
# KEEP SUCCESSFUL RUNS
# ============================================================

success_df = df[df["Status"] == "SUCCESS"].copy()


# ============================================================
# CALCULATE SUMMARY
# ============================================================

summary_rows = []

for benchmark in df["Benchmark Type"].unique():

    benchmark_data = df[
        df["Benchmark Type"] == benchmark
    ]

    successful_data = benchmark_data[
        benchmark_data["Status"] == "SUCCESS"
    ]

    total_runs = len(benchmark_data)

    successful_runs = len(successful_data)

    failed_runs = total_runs - successful_runs

    if successful_runs > 0:

        latencies = successful_data["Latency (ms)"]

        minimum = latencies.min()
        maximum = latencies.max()
        p50 = latencies.median()
        p95 = latencies.quantile(0.95)

    else:

        minimum = None
        maximum = None
        p50 = None
        p95 = None

    success_rate = (
        successful_runs / total_runs
    ) * 100

    failure_rate = (
        failed_runs / total_runs
    ) * 100

    summary_rows.append({

        "Benchmark Type": benchmark,

        "Total Runs": total_runs,

        "Successful Runs": successful_runs,

        "Failed Runs": failed_runs,

        "Success Rate (%)": success_rate,

        "Failure Rate (%)": failure_rate,

        "Minimum Latency (ms)": minimum,

        "Maximum Latency (ms)": maximum,

        "P50 Latency (ms)": p50,

        "P95 Latency (ms)": p95

    })


# ============================================================
# CREATE SUMMARY DATAFRAME
# ============================================================

summary = pd.DataFrame(summary_rows)

summary = summary.round(3)


print()
print("============================================================")
print("COGNODB BENCHMARK SUMMARY")
print("============================================================")
print()

print(summary.to_string(index=False))


# ============================================================
# SAVE SUMMARY CSV
# ============================================================

SUMMARY_FILE = "benchmark_summary.csv"

summary.to_csv(
    SUMMARY_FILE,
    index=False
)

print()
print(
    f"Summary CSV created successfully: "
    f"{SUMMARY_FILE}"
)


# ============================================================
# GRAPH 1 - P50 LATENCY
# ============================================================

plt.figure(figsize=(8, 5))

plt.bar(
    summary["Benchmark Type"],
    summary["P50 Latency (ms)"]
)

plt.title("CognoDB Benchmark - P50 Latency")

plt.xlabel("Benchmark Type")

plt.ylabel("Latency (ms)")

plt.tight_layout()

plt.savefig(
    "p50_latency.png"
)

plt.close()


# ============================================================
# GRAPH 2 - P95 LATENCY
# ============================================================

plt.figure(figsize=(8, 5))

plt.bar(
    summary["Benchmark Type"],
    summary["P95 Latency (ms)"]
)

plt.title("CognoDB Benchmark - P95 Latency")

plt.xlabel("Benchmark Type")

plt.ylabel("Latency (ms)")

plt.tight_layout()

plt.savefig(
    "p95_latency.png"
)

plt.close()


# ============================================================
# GRAPH 3 - LATENCY BY RUN
# ============================================================

plt.figure(figsize=(10, 6))

for benchmark in success_df["Benchmark Type"].unique():

    benchmark_data = success_df[
        success_df["Benchmark Type"] == benchmark
    ]

    plt.plot(
        benchmark_data["Run Number"],
        benchmark_data["Latency (ms)"],
        marker="o",
        label=benchmark
    )


plt.title(
    "CognoDB Benchmark Latency by Run"
)

plt.xlabel("Run Number")

plt.ylabel("Latency (ms)")

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "latency_by_run.png"
)

plt.close()


# ============================================================
# GRAPH 4 - SUCCESS VS FAILURE
# ============================================================

plt.figure(figsize=(8, 5))

x = range(len(summary))

plt.bar(
    summary["Benchmark Type"],
    summary["Successful Runs"],
    label="Successful Runs"
)

plt.bar(
    summary["Benchmark Type"],
    summary["Failed Runs"],
    bottom=summary["Successful Runs"],
    label="Failed Runs"
)

plt.title(
    "CognoDB Benchmark Success and Failure"
)

plt.xlabel("Benchmark Type")

plt.ylabel("Number of Runs")

plt.legend()

plt.tight_layout()

plt.savefig(
    "success_failure.png"
)

plt.close()


# ============================================================
# FINISH
# ============================================================

print()
print("============================================================")
print("ANALYSIS COMPLETED SUCCESSFULLY")
print("============================================================")

print()
print("Files created:")

print("1. benchmark_summary.csv")
print("2. p50_latency.png")
print("3. p95_latency.png")
print("4. latency_by_run.png")
print("5. success_failure.png")