import os
import subprocess

def run_migrations(env):
    os.environ["ALEMBIC_ENV"] = env
    subprocess.run(["alembic", "upgrade", "head"], check=True)

if __name__ == "__main__":
    print("Running migrations for default database...")
    run_migrations("default")
    
    print("Running migrations for test database...")
    run_migrations("test")