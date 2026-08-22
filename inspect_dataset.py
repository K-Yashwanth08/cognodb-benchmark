import csv

FILE = "git_web_ml/git_web_ml/musae_git_edges.csv"

nodes = set()
edge_count = 0
duplicate_edges = 0
self_loops = 0
seen_edges = set()

with open(FILE, "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        source = int(row["id_1"])
        target = int(row["id_2"])

        edge_count += 1

        nodes.add(source)
        nodes.add(target)

        if source == target:
            self_loops += 1

        edge = (source, target)

        if edge in seen_edges:
            duplicate_edges += 1

        seen_edges.add(edge)

print("Dataset inspection")
print("------------------")
print("Edges:", edge_count)
print("Unique nodes:", len(nodes))
print("Duplicate edges:", duplicate_edges)
print("Self-loops:", self_loops)