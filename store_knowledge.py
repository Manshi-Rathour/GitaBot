import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PostgreSQL Connection Details (Read from .env)
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    print("✅ Connected to PostgreSQL successfully!")
except Exception as e:
    print("❌ Error connecting to the database:", e)
    exit()

# Step 1: Create the table if it does not exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_content TEXT NOT NULL
);
""")
conn.commit()
print("✅ Table 'knowledge_base' is ready!")

# Step 2: Define the knowledge base directory
knowledge_base_dir = "knowledge_base"

if not os.path.exists(knowledge_base_dir):
    print(f"❌ Directory '{knowledge_base_dir}' not found!")
    exit()

# Step 3: Upload all .txt files from subdirectories
file_count = 0

for root, _, files in os.walk(knowledge_base_dir):
    for file in files:
        if file.endswith(".txt"):
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, knowledge_base_dir)  # Store relative path

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()

                # Insert data into PostgreSQL
                cursor.execute(
                    "INSERT INTO knowledge_base (file_name, file_content) VALUES (%s, %s)",
                    (relative_path, content)
                )
                file_count += 1

            except Exception as e:
                print(f"❌ Error reading '{file_path}': {e}")

conn.commit()
print(f"✅ {file_count} files uploaded successfully!")

# Step 4: Retrieve a specific file content from the database
search_file = "Season_05/Peace_Formula.txt"  # Example file lookup
cursor.execute("SELECT file_content FROM knowledge_base WHERE file_name = %s", (search_file,))
result = cursor.fetchone()

if result:
    print(f"\n📄 Content of '{search_file}':\n", result[0])
else:
    print(f"❌ File '{search_file}' not found in the database.")

# Close connection
cursor.close()
conn.close()
print("✅ Database connection closed.")
