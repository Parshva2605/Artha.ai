import sys
import os
sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
))

from backend.database.db import engine
from backend.database.models import Base

def run_migrations():
    print("Running Artha AI migrations...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully:")
    for table in Base.metadata.tables.keys():
        print(f"  - {table}")
    print("Migration complete.")

if __name__ == "__main__":
    run_migrations()
