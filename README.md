 CognoDB Graph Database Benchmark

 1. Project Objective

    This project evaluates the performance of the CognoDB graph database for different graph query patterns.
    
    The benchmark measures query latency and reliability for:
    
    - Point Lookup
    - 1-Hop Traversal
    - 2-Hop Traversal
    - 3-Hop Traversal
    
    The objective is to understand how query performance changes as graph traversal depth and the number of reachable users increase.


2. CognoDB Setup

      The project uses CognoDB as the graph database.
      
      The Python application connects to CognoDB using the Neo4j Python driver.
      
        Technologies Used
        
        - Python
        - CognoDB
        - Neo4j Python Driver
        - Pandas
        - Matplotlib
        - python-dotenv
      
      Connection Configuration
      
      Database credentials are stored securely in a `.env` file.
      
        env
        COGNODB_URI=your_database_uri
        COGNODB_USERNAME=your_username
        COGNODB_PASSWORD=your_password

3. Dataset and Graph Structure

      The database contains users represented as graph nodes.
      
      Example node:
      
      (:User {
          id: user_id
      })
      
      Users are connected using the following relationship:
      
      (:User)-[:CONNECTED_TO]->(:User)
      
      The benchmark uses the following test user IDs:
      
          0, 1, 2, 3, 4, 10, 20, 30, 40, 50
      
      Different users have different numbers of connected and reachable users. This allows the benchmark to test graph traversal performance at different scales.


   4. Benchmark Methodology

      Each benchmark type is executed 10 times.
      
      Before the benchmark begins, 5 warm-up queries are executed.
      
      The following metrics are measured:
      
          Minimum latency
          Maximum latency
          P50 latency
          P95 latency
          Success rate
          Failure rate
      
      The benchmark also includes retry and reconnection logic to handle temporary database connection failures.
      
      Point Lookup
          MATCH (u:User {id: $user_id})
          RETURN u.id AS id
      1-Hop Traversal
          MATCH (u:User {id: $user_id})
                -[:CONNECTED_TO]->(neighbor)
          RETURN count(neighbor) AS count
      2-Hop Traversal
          MATCH (u:User {id: $user_id})
                -[:CONNECTED_TO*2]->(neighbor)
          RETURN count(DISTINCT neighbor) AS count
      3-Hop Traversal
          MATCH (u:User {id: $user_id})
                -[:CONNECTED_TO*3]->(neighbor)
          RETURN count(DISTINCT neighbor) AS count

5. Benchmark Results


6. Point Lookup Results

  Point Lookup showed stable performance.

    Results
    Success Rate: 100%
    Minimum Latency: 259.063 ms
    P50 Latency: 271.312 ms
    P95 Latency: 293.540 ms
    Maximum Latency: 303.112 ms

  The Point Lookup benchmark remained relatively stable across all runs.

7. 1-Hop Results

    The 1-Hop traversal retrieves users directly connected to the selected user.
    
    Results
    Success Rate: 100%
    Minimum Latency: 264.528 ms
    P50 Latency: 276.706 ms
    P95 Latency: 294.147 ms
    Maximum Latency: 294.667 ms
    
    The 1-Hop queries showed stable performance even when the number of neighbors varied.

8. 2-Hop Results

    The 2-Hop traversal explores users reachable through two graph connections.
    
    Results
    Success Rate: 100%
    Minimum Latency: 270.146 ms
    P50 Latency: 282.582 ms
    P95 Latency: 376.923 ms
    Maximum Latency: 401.384 ms
    
    Latency increased compared to Point Lookup and 1-Hop queries as the traversal depth and number of reachable users increased.

9. 3-Hop Results

    The 3-Hop traversal produced the highest latency because it explores a significantly larger portion of the graph.
    
    Results
    Success Rate: 90%
    Failed Runs: 1
    Minimum Latency: 288.872 ms
    P50 Latency: 838.811 ms
    P95 Latency: 4251.350 ms
    Maximum Latency: 4879.124 ms
    
    The largest observed traversal involved:
    
    User ID: 30
    Reachable Users: 13,386
    Latency: 4,879.124 ms

10. Benchmark Graphs

    P50 Latency
    
    P95 Latency
    
    Latency by Run
    
    Success vs Failure

12. Key Findings

    The benchmark produced the following observations:
    
    Point Lookup queries were stable, with a P50 latency of approximately 271 ms.
    1-Hop queries maintained stable performance, with 100% successful execution.
    2-Hop queries showed slightly increased latency, particularly for users with a larger number of reachable nodes.
    3-Hop queries had significantly higher latency variability.
    The largest 3-Hop traversal reached 13,386 users and required approximately 4.88 seconds.
    The 3-Hop benchmark achieved a 90% success rate, with one query failing due to a database connection issue.
    The results indicate that graph traversal depth and graph expansion size have a significant impact on query performance.

13. Generated Benchmark Files

    The benchmark generates the following files:
    
    benchmark_results.csv
    
    Contains individual benchmark runs with:
    
    Benchmark Type
    Run Number
    User ID
    Result Count
    Latency
    Status
    benchmark_summary.csv
    
    Contains the summarized benchmark statistics, including:
    
    Total Runs
    Successful Runs
    Failed Runs
    Success Rate
    Failure Rate
    Minimum Latency
    Maximum Latency
    P50 Latency
    P95 Latency

3. How to Run
    Clone the Repository
        git clone https://github.com/K-Yashwanth08/cognodb-benchmark.git
    Navigate to the Project Directory
       cd cognodb-benchmark
    Create and Activate a Virtual Environment
        python -m venv .venv
        .venv\Scripts\Activate.ps1
    Install Dependencies
        python -m pip install -r requirements.txt

    Configure Environment Variables
    Create a .env file and add:
    
        COGNODB_URI=your_database_uri
        COGNODB_USERNAME=your_username
        COGNODB_PASSWORD=your_password
    Run the Benchmark
       python run_benchmark.py
    Analyze Results
       python analyze_results.py

14. Conclusion

    This project successfully benchmarks CognoDB graph query performance across different traversal depths.
    The results show that Point Lookup, 1-Hop, and 2-Hop queries provided relatively stable performance with a 100% success rate during this benchmark run.
    The 3-Hop traversal demonstrates the impact of graph expansion on performance. As the number of reachable users increases, query latency becomes more variable and significantly higher.
    The benchmark framework also includes warm-up queries, retry logic, connection recovery, CSV result storage, statistical analysis, and visualization generation.
    This provides a reproducible framework for evaluating CognoDB graph traversal performance.
