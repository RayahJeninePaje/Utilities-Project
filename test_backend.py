
from database import create_tables, register_user, connect_db, save_record, get_records
from generator import generate_multiple_users

# Create database tables
create_tables()

# Create a test account if it doesn't exist
username = "demo_user"
password = "Demo123!"

register_user(username, password)

# Get the test user's ID
conn = connect_db()
cursor = conn.cursor()

cursor.execute(
    "SELECT id FROM users WHERE username = ?",
    (username,)
)

user_id = cursor.fetchone()[0]
conn.close()

# Generate 10 fake users
records = generate_multiple_users(10)

# Save generated records
for record in records:
    save_record(user_id, record)

# Retrieve saved records
saved_records = get_records(user_id)

print("================================")
print("DATAGEN BACKEND TEST")
print("================================")
print(f"Successfully generated and stored {len(saved_records)} records!")

for record in saved_records:
    print(record)
