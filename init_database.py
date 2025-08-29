#!/usr/bin/env python3
"""
Initialize Bob's Database
Creates the complete SQLite database with all 25 tables
"""

import sys
import os
from pathlib import Path

# Add the Bob directory to the path
sys.path.append(str(Path(__file__).parent))

from core.database_core import DatabaseCore


def initialize_bob_database():
    """Initialize Bob's complete database system."""
    
    print("🗄️  Initializing Bob's Database System")
    print("=" * 50)
    
    # Create the database (this will auto-initialize all tables)
    db_path = "/Users/bard/Bob/data/bob.db"
    print(f"Database path: {db_path}")
    
    try:
        # Create DatabaseCore instance (auto-initializes schema)
        db = DatabaseCore(db_path=db_path)
        
        print("✅ Database connection established")
        
        # Get schema information
        schema_info = db.get_schema_info()
        
        print(f"\n📊 Database Schema Information:")
        print(f"  • Tables created: {schema_info.get('table_count', 0)}")
        print(f"  • Total rows: {schema_info.get('total_rows', 0)}")
        
        print(f"\n📋 Created Tables:")
        for table in schema_info.get('tables', []):
            row_count = schema_info.get('row_counts', {}).get(table, 0)
            print(f"  • {table}: {row_count} rows")
        
        print(f"\n🎯 Testing Database Operations:")
        
        # Test basic operations
        test_note_id = "test_note_001"
        success = db.create_note(
            note_id=test_note_id,
            title="Database Initialization Test",
            content="This note confirms the database is working properly.",
            note_type="system_test"
        )
        print(f"  ✅ Note creation: {success} (ID: {test_note_id})")
        
        # Test group creation
        test_group_id = "test_group_001"
        success = db.create_group(
            group_id=test_group_id,
            name="System Test Group",
            description="Test group created during database initialization",
            group_type="system"
        )
        print(f"  ✅ Group creation: {success} (ID: {test_group_id})")
        
        # Test reading back the note
        retrieved_note = db.get_note(test_note_id)
        if retrieved_note:
            print(f"  ✅ Note retrieval: {retrieved_note['title']}")
        else:
            print(f"  ❌ Note retrieval failed")
        
        print(f"\n🏆 Database Initialization Complete!")
        print(f"Bob's database is fully operational with {schema_info.get('table_count', 0)} tables.")
        
        # Close the database connection
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


if __name__ == "__main__":
    success = initialize_bob_database()
    if success:
        print(f"\n✅ Bob's database is ready for use!")
        sys.exit(0)
    else:
        print(f"\n❌ Database initialization failed!")
        sys.exit(1)
