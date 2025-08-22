"""
Test suite for DatabaseCore module.

Tests all functionality of Bob's comprehensive database schema including:
- CRUD operations for notes, memories, state
- Group management and hierarchies  
- Tool usage tracking and analytics
- Graph relationships with metadata
- Schema validation and performance
"""

import tempfile
import json
import os
from pathlib import Path
import sys

# Add the parent directory to sys.path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database_core import DatabaseCore


class TestDatabaseCore:
    """Comprehensive test suite for DatabaseCore."""
    
    def setup_method(self):
        """Setup test database for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_bob.db")
        self.db = DatabaseCore(self.db_path)
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.db.close()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_initialization(self):
        """Test that database initializes with correct schema."""
        schema_info = self.db.get_schema_info()
        
        # Check that all expected tables are created
        expected_tables = [
            'notes', 'memories', 'state', 'groups', 'group_memberships',
            'group_hierarchies', 'group_permissions', 'group_meta',
            'tool_usage', 'protocol_executions', 'tool_effectiveness',
            'protocol_patterns', 'edges', 'edge_meta', 'node_meta',
            'graph_snapshots', 'sessions', 'interactions', 'reflections',
            'contexts', 'assembly_queue', 'generation_history',
            'assessment_results', 'performance_metrics', 'usage_analytics'
        ]
        
        assert schema_info['table_count'] == len(expected_tables)
        for table in expected_tables:
            assert table in schema_info['tables']
        
        # All tables should start empty
        assert schema_info['total_rows'] == 0
    
    def test_note_crud_operations(self):
        """Test complete CRUD operations for notes."""
        # Create
        success = self.db.create_note(
            note_id="test_note_1",
            title="Test Note",
            content="This is test content",
            note_type="test",
            tags=["testing", "crud"],
            metadata={"priority": "high", "category": "test"}
        )
        assert success
        
        # Read
        note = self.db.get_note("test_note_1")
        assert note is not None
        assert note['title'] == "Test Note"
        assert note['content'] == "This is test content"
        assert note['type'] == "test"
        assert note['tags'] == ["testing", "crud"]
        assert note['metadata']['priority'] == "high"
        
        # Update
        success = self.db.update_note(
            "test_note_1",
            content="Updated content",
            tags=["testing", "crud", "updated"]
        )
        assert success
        
        updated_note = self.db.get_note("test_note_1")
        assert updated_note['content'] == "Updated content"
        assert "updated" in updated_note['tags']
        
        # List
        notes = self.db.list_notes(note_type="test")
        assert len(notes) == 1
        assert notes[0]['id'] == "test_note_1"
        
        # Delete
        success = self.db.delete_note("test_note_1")
        assert success
        
        deleted_note = self.db.get_note("test_note_1")
        assert deleted_note is None
    
    def test_group_management(self):
        """Test group creation and membership management."""
        # Create a group
        success = self.db.create_group(
            group_id="test_group",
            name="Test Group",
            description="A group for testing",
            group_type="test",
            metadata={"purpose": "testing"}
        )
        assert success
        
        # Create some notes to add to the group
        self.db.create_note("note1", "Note 1", content="Content 1")
        self.db.create_note("note2", "Note 2", content="Content 2")
        
        # Add notes to group
        success = self.db.add_to_group("test_group", "note", "note1")
        assert success
        
        success = self.db.add_to_group("test_group", "note", "note2", role="admin")
        assert success
        
        # Get group members
        members = self.db.get_group_members("test_group")
        assert len(members) == 2
        
        note_members = self.db.get_group_members("test_group", entity_type="note")
        assert len(note_members) == 2
        
        # Check roles
        admin_members = [m for m in members if m['role'] == 'admin']
        assert len(admin_members) == 1
        assert admin_members[0]['entity_id'] == 'note2'
    
    def test_tool_usage_tracking(self):
        """Test tool usage logging and analytics."""
        # Log some tool usage
        usage_id1 = self.db.log_tool_usage(
            tool_name="test_tool",
            parameters={"param1": "value1"},
            execution_time_ms=150,
            success=True,
            effectiveness_rating=0.9,
            context={"session": "test_session"}
        )
        assert usage_id1
        
        usage_id2 = self.db.log_tool_usage(
            tool_name="test_tool",
            parameters={"param1": "value2"},
            execution_time_ms=200,
            success=False,
            error_message="Test error",
            effectiveness_rating=0.3
        )
        assert usage_id2
        
        usage_id3 = self.db.log_tool_usage(
            tool_name="other_tool",
            execution_time_ms=100,
            success=True,
            effectiveness_rating=0.8
        )
        assert usage_id3
        
        # Get tool usage stats
        all_stats = self.db.get_tool_usage_stats()
        assert len(all_stats) == 2  # test_tool and other_tool
        
        test_tool_stats = self.db.get_tool_usage_stats("test_tool")
        assert len(test_tool_stats) == 1
        stats = test_tool_stats[0]
        assert stats['tool_name'] == 'test_tool'
        assert stats['usage_count'] == 2
        assert stats['avg_time'] == 175.0  # (150 + 200) / 2
        assert stats['success_rate'] == 50.0  # 1 success out of 2
        assert abs(stats['avg_effectiveness'] - 0.6) < 0.01  # (0.9 + 0.3) / 2
    
    def test_graph_operations(self):
        """Test graph edge creation and retrieval."""
        # Create some entities first
        self.db.create_note("note1", "Note 1")
        self.db.create_note("note2", "Note 2")
        
        # Create edges
        success = self.db.create_edge(
            from_entity_type="note",
            from_entity_id="note1",
            to_entity_type="note", 
            to_entity_id="note2",
            relationship_type="references",
            weight=0.8,
            metadata={"confidence": 0.9, "created_by": "system"}
        )
        assert success
        
        success = self.db.create_edge(
            from_entity_type="note",
            from_entity_id="note2",
            to_entity_type="note",
            to_entity_id="note1", 
            relationship_type="similar_to",
            weight=0.7,
            bidirectional=True
        )
        assert success
        
        # Get edges for note1
        note1_edges = self.db.get_edges("note", "note1")
        assert len(note1_edges) == 2  # Both edges should include note1
        
        # Get edges by relationship type
        ref_edges = self.db.get_edges(relationship_type="references")
        assert len(ref_edges) == 1
        assert ref_edges[0]['relationship_type'] == 'references'
        assert ref_edges[0]['weight'] == 0.8
    
    def test_edge_metadata(self):
        """Test edge metadata functionality."""
        # Create an edge first
        self.db.create_note("note1", "Note 1")
        self.db.create_note("note2", "Note 2")
        
        self.db.create_edge("note", "note1", "note", "note2", "test_relation")
        
        # Get the edge to find its ID
        edges = self.db.get_edges("note", "note1")
        assert len(edges) > 0
        edge_id = edges[0]['id']
        
        # Set edge metadata
        success = self.db.set_edge_meta(edge_id, "strength", 0.95)
        assert success
        
        success = self.db.set_edge_meta(edge_id, "created_by", "test_system")
        assert success
        
        success = self.db.set_edge_meta(edge_id, "complex_data", {"nested": {"value": 42}})
        assert success
        
        # Verify metadata was stored (would need additional method to retrieve)
        # For now, we verify no errors occurred during storage
    
    def test_custom_queries(self):
        """Test custom query execution."""
        # Add some test data
        self.db.create_note("note1", "Note 1", note_type="important")
        self.db.create_note("note2", "Note 2", note_type="draft")
        self.db.create_note("note3", "Note 3", note_type="important")
        
        # Execute custom query
        results = self.db.execute_query("""
            SELECT type, COUNT(*) as count 
            FROM notes 
            WHERE archived = FALSE 
            GROUP BY type
            ORDER BY count DESC
        """)
        
        assert len(results) == 2
        # Should have 2 important notes and 1 draft
        important_count = next(r['count'] for r in results if r['type'] == 'important')
        draft_count = next(r['count'] for r in results if r['type'] == 'draft')
        
        assert important_count == 2
        assert draft_count == 1
    
    def test_transaction_safety(self):
        """Test that transactions work correctly for error handling."""
        # This test simulates a transaction failure
        try:
            with self.db.transaction() as conn:
                # Create a note
                conn.execute("""
                    INSERT INTO notes (id, title, content) 
                    VALUES (?, ?, ?)
                """, ("test_note", "Test", "Content"))
                
                # Force an error with invalid SQL
                conn.execute("INVALID SQL STATEMENT")
        except Exception:
            pass  # Expected to fail
        
        # Verify the note was not created due to rollback
        note = self.db.get_note("test_note")
        assert note is None
    
    def test_json_field_handling(self):
        """Test proper JSON serialization/deserialization."""
        # Create note with complex metadata
        complex_metadata = {
            "nested": {"deep": {"value": 42}},
            "array": [1, 2, 3],
            "boolean": True,
            "null_value": None
        }
        
        success = self.db.create_note(
            "json_test",
            "JSON Test",
            metadata=complex_metadata
        )
        assert success
        
        # Retrieve and verify JSON was preserved
        note = self.db.get_note("json_test")
        assert note['metadata'] == complex_metadata
        assert note['metadata']['nested']['deep']['value'] == 42
        assert note['metadata']['array'] == [1, 2, 3]
        assert note['metadata']['boolean'] is True
        assert note['metadata']['null_value'] is None


def run_tests():
    """Run all tests manually (for environments without pytest)."""
    import traceback
    
    test_instance = TestDatabaseCore()
    test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        try:
            print(f"Running {test_method}...")
            test_instance.setup_method()
            getattr(test_instance, test_method)()
            test_instance.teardown_method()
            print(f"✓ {test_method} passed")
            passed += 1
        except Exception as e:
            print(f"✗ {test_method} failed: {e}")
            traceback.print_exc()
            failed += 1
            try:
                test_instance.teardown_method()
            except:
                pass
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    # Run tests if executed directly
    success = run_tests()
    exit(0 if success else 1)
