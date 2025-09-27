import sqlite3
from unittest.mock import patch, mock_open
from db.migrate import get_applied_migrations, apply_migration, main


class TestMigrate:
    """Tests for the migration system."""

    def test_get_applied_migrations_creates_table(self):
        """
        Test that get_applied_migrations creates the schema_migrations table and returns empty set.
        
        This test verifies the basic functionality of the get_applied_migrations function:
        1. It should create the schema_migrations table if it doesn't exist
        2. It should return an empty set when no migrations have been applied yet
        3. The table should have the correct structure (filename and applied_at columns)
        """
        # Create an in-memory database for testing
        # This avoids file system issues and is faster than real files
        conn = sqlite3.connect(":memory:")
        
        # Enable row factory so we can access columns by name instead of index
        # This makes the code more readable: row['filename'] instead of row[0]
        conn.row_factory = sqlite3.Row
        
        try:
            # Call the function under test
            # This should create the schema_migrations table if it doesn't exist
            applied_migrations = get_applied_migrations(conn)
            
            # Since this is a fresh database, no migrations should be applied yet
            # The function should return an empty set
            assert applied_migrations == set()
            
            # Verify that the schema_migrations table was actually created
            # PRAGMA table_info returns metadata about table columns
            cursor = conn.execute("PRAGMA table_info(schema_migrations)")
            table_columns = cursor.fetchall()
            
            # Extract just the column names for easier checking
            column_names = [row['name'] for row in table_columns]
            
            # The table should have both required columns
            assert 'filename' in column_names, "schema_migrations table should have 'filename' column"
            assert 'applied_at' in column_names, "schema_migrations table should have 'applied_at' column"
            
        finally:
            # Always close the database connection to prevent resource leaks
            conn.close()

    def test_apply_migration_executes_sql_and_records(self):
        """
        Test that apply_migration executes SQL and records the migration in schema_migrations.
        
        This test verifies the core migration application functionality:
        1. It should execute the provided SQL statements
        2. It should record the migration filename in schema_migrations table
        3. It should commit the changes to the database
        4. The executed SQL should actually create/modify database objects
        """
        # Create an in-memory database for testing
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        
        try:
            # First, create the schema_migrations table manually
            # This simulates a database that already has the migration tracking table
            conn.execute("""
                CREATE TABLE schema_migrations (
                    filename TEXT PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
            # Define test SQL that will create a new table
            # This is what would be in a real migration file
            test_sql = "CREATE TABLE test_users (id INTEGER PRIMARY KEY, name TEXT);"
            migration_filename = "001_create_users.sql"
            
            # Call the function under test
            # This should execute the SQL and record the migration
            apply_migration(conn, migration_filename, test_sql)
            
            # Verify that the SQL was actually executed
            # Check if the table was created by querying sqlite_master
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='test_users'
            """)
            table_exists = cursor.fetchone() is not None
            assert table_exists, "The test_users table should have been created by the migration"
            
            # Verify that the migration was recorded in schema_migrations table
            cursor = conn.execute("SELECT filename FROM schema_migrations")
            recorded_migrations = [row['filename'] for row in cursor.fetchall()]
            assert migration_filename in recorded_migrations, f"Migration {migration_filename} should be recorded in schema_migrations"
            
            # Verify that only our migration is recorded (no duplicates)
            assert len(recorded_migrations) == 1, "Should have exactly one recorded migration"
            assert recorded_migrations[0] == migration_filename, "Recorded migration should match the applied one"
            
        finally:
            # Always close the database connection to prevent resource leaks
            conn.close()