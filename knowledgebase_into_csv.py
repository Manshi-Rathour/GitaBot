import os
import csv

# Define the knowledge base folder path
knowledge_base_dir = "knowledge_base"

# Output CSV file
csv_filename = "knowledge_base.csv"

# Collect data from txt files
data = []

# Traverse through all season folders and txt files
for root, _, files in os.walk(knowledge_base_dir):
    for file in files:
        if file.endswith(".txt"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                relative_path = os.path.relpath(file_path, knowledge_base_dir)
                data.append([relative_path, content])
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

# Save data to CSV
with open(csv_filename, "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["file_name", "file_content"])  # Header
    writer.writerows(data)

print(f"CSV file '{csv_filename}' created successfully with {len(data)} entries.")
