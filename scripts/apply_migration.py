"""Apply one named MySQL migration exactly once."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import get_db_connection


def apply_migration(migration_path: str) -> None:
    path = Path(migration_path)
    version = path.stem
    statements = [
        statement.strip()
        for statement in path.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(100) PRIMARY KEY,
                applied_at DATETIME(6) NOT NULL
            )
            """
        )
        connection.commit()
        cursor.execute(
            "SELECT 1 FROM schema_migrations WHERE version = %s",
            (version,),
        )
        if cursor.fetchone():
            print(f"Migration already applied: {version}")
            return

        for statement in statements:
            if statement.startswith("INSERT INTO schema_migrations"):
                cursor.execute(
                    """
                    INSERT INTO schema_migrations (version, applied_at)
                    VALUES (%s, UTC_TIMESTAMP(6))
                    """,
                    (version,),
                )
            else:
                cursor.execute(statement)
        connection.commit()
        print(f"Migration applied: {version}")
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    apply_migration(sys.argv[1])
