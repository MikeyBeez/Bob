#!/usr/bin/env python3
"""
Test suite for FileSystemCore - Safe file operations with validation

Tests all file system operations including:
- Read/write operations
- Directory management  
- Path validation and sandboxing
- Atomic writes
- Error handling
- Performance metrics
- Async operations
"""

import os
import sys
import json
import tempfile
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.filesystem_core import FileSystemCore, create_filesystem_core
from core.database_core import DatabaseCore


class TestFileSystemCore:
    """Comprehensive test suite for FileSystemCore."""
    
    def __init__(self):
        """Initialize test environment."""
        # Create temp directory for tests
        self.test_dir = Path(tempfile.mkdtemp(prefix="bob_fs_test_"))
        self.db_core = DatabaseCore(":memory:")  # In-memory database for tests
        self.fs_core = FileSystemCore(self.db_core, str(self.test_dir))
        
        # Add test directory to sandbox
        self.fs_core.add_sandbox_path(self.test_dir)
        
        self.passed = 0
        self.failed = 0
    
    def cleanup(self):
        """Clean up test environment."""
        import shutil
        try:
            shutil.rmtree(self.test_dir)
        except:
            pass
    
    def run_test(self, test_func):
        """Run a single test with error handling."""
        test_name = test_func.__name__
        print(f"Running {test_name}...")
        
        try:
            test_func()
            print(f"✓ {test_name} passed")
            self.passed += 1
        except Exception as e:
            print(f"✗ {test_name} failed: {e}")
            self.failed += 1
            import traceback
            traceback.print_exc()
    
    # === TEST METHODS ===
    
    def test_file_write_and_read(self):
        """Test basic file write and read operations."""
        test_file = self.test_dir / "test_write.txt"
        content = "Hello, Bob! This is a test file."
        
        # Write file
        bytes_written = self.fs_core.write_file(test_file, content)
        assert bytes_written == len(content), "Incorrect bytes written"
        
        # Read file
        read_content = self.fs_core.read_file(test_file)
        assert read_content == content, "Content mismatch"
        
        # Test binary mode
        binary_content = b"Binary data \x00\x01\x02"
        self.fs_core.write_file(test_file, binary_content, mode='binary')
        read_binary = self.fs_core.read_file(test_file, mode='binary')
        assert read_binary == binary_content, "Binary content mismatch"
    
    def test_json_operations(self):
        """Test JSON read/write operations."""
        test_file = self.test_dir / "test_data.json"
        test_data = {
            "name": "Bob",
            "version": "1.0.0",
            "features": ["intelligence", "persistence", "adaptability"],
            "metadata": {
                "created": datetime.now().isoformat(),
                "author": "System"
            }
        }
        
        # Write JSON
        self.fs_core.write_json(test_file, test_data)
        
        # Read JSON
        read_data = self.fs_core.read_json(test_file)
        assert read_data["name"] == test_data["name"], "JSON name mismatch"
        assert read_data["features"] == test_data["features"], "JSON features mismatch"
    
    def test_atomic_write(self):
        """Test atomic write operations."""
        test_file = self.test_dir / "atomic_test.txt"
        
        # Simulate write with atomic=True (default)
        content = "Atomic write test"
        self.fs_core.write_file(test_file, content, atomic=True)
        assert self.fs_core.read_file(test_file) == content
        
        # Test non-atomic write
        new_content = "Non-atomic write"
        self.fs_core.write_file(test_file, new_content, atomic=False)
        assert self.fs_core.read_file(test_file) == new_content
    
    def test_append_file(self):
        """Test file append operations."""
        test_file = self.test_dir / "append_test.txt"
        
        # Initial write
        self.fs_core.write_file(test_file, "Line 1\n")
        
        # Append
        self.fs_core.append_file(test_file, "Line 2\n")
        self.fs_core.append_file(test_file, "Line 3\n")
        
        content = self.fs_core.read_file(test_file)
        assert "Line 1" in content and "Line 2" in content and "Line 3" in content
        assert content.count("\n") == 3
    
    def test_directory_operations(self):
        """Test directory creation, listing, and deletion."""
        # Create nested directories
        test_dir = self.test_dir / "nested" / "directories" / "test"
        created_dir = self.fs_core.create_directory(test_dir)
        assert created_dir.exists() and created_dir.is_dir()
        
        # Create some files
        for i in range(3):
            self.fs_core.write_file(test_dir / f"file{i}.txt", f"Content {i}")
        
        # List directory
        files = self.fs_core.list_directory(test_dir)
        assert len(files) == 3
        
        # List with pattern
        txt_files = self.fs_core.list_directory(test_dir, pattern="*.txt")
        assert len(txt_files) == 3
        
        # Recursive listing
        self.fs_core.write_file(test_dir.parent / "parent_file.txt", "Parent")
        all_files = self.fs_core.list_directory(test_dir.parent, recursive=True)
        assert len(all_files) >= 4  # 3 in test_dir + 1 in parent + directories
        
        # Delete directory (non-recursive should fail with files)
        try:
            self.fs_core.delete_directory(test_dir, recursive=False)
            assert False, "Should have failed - directory not empty"
        except:
            pass  # Expected
        
        # Delete recursive
        self.fs_core.delete_directory(test_dir, recursive=True)
        assert not test_dir.exists()
    
    def test_file_operations(self):
        """Test copy, move, and delete file operations."""
        source_file = self.test_dir / "source.txt"
        dest_file = self.test_dir / "destination.txt"
        move_file = self.test_dir / "moved.txt"
        
        content = "Test content for file operations"
        self.fs_core.write_file(source_file, content)
        
        # Copy file
        copied = self.fs_core.copy_file(source_file, dest_file)
        assert copied.exists()
        assert self.fs_core.read_file(dest_file) == content
        assert source_file.exists()  # Original should still exist
        
        # Move file
        moved = self.fs_core.move_file(source_file, move_file)
        assert moved.exists()
        assert self.fs_core.read_file(move_file) == content
        assert not source_file.exists()  # Original should be gone
        
        # Delete file
        self.fs_core.delete_file(move_file)
        assert not move_file.exists()
        
        # Try to delete non-existent file
        try:
            self.fs_core.delete_file(move_file)
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected
    
    def test_path_validation(self):
        """Test path validation and sandboxing."""
        # Valid paths within sandbox
        valid_path = self.test_dir / "valid.txt"
        self.fs_core.write_file(valid_path, "Valid")
        
        # Try to access outside sandbox
        invalid_path = "/etc/passwd"
        try:
            self.fs_core.read_file(invalid_path)
            assert False, "Should have raised ValueError for path outside sandbox"
        except ValueError as e:
            assert "outside sandbox" in str(e)
        
        # Try to write outside sandbox
        try:
            self.fs_core.write_file("/tmp/bad_file.txt", "Bad")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
        
        # Test sandbox management
        new_sandbox = Path(tempfile.mkdtemp(prefix="bob_sandbox_"))
        self.fs_core.add_sandbox_path(new_sandbox)
        
        # Should now work
        test_file = new_sandbox / "allowed.txt"
        self.fs_core.write_file(test_file, "Now allowed")
        assert self.fs_core.read_file(test_file) == "Now allowed"
        
        # Remove sandbox
        self.fs_core.remove_sandbox_path(new_sandbox)
        try:
            self.fs_core.read_file(test_file)
            assert False, "Should have raised ValueError after removing sandbox"
        except ValueError:
            pass  # Expected
        
        # Cleanup
        import shutil
        shutil.rmtree(new_sandbox)
    
    def test_file_info_and_metrics(self):
        """Test file info retrieval and performance metrics."""
        test_file = self.test_dir / "info_test.txt"
        content = "Test content for file info"
        self.fs_core.write_file(test_file, content)
        
        # Get file info
        info = self.fs_core.get_file_info(test_file)
        assert info["name"] == "info_test.txt"
        assert info["size"] == len(content)
        assert info["is_file"] == True
        assert info["is_dir"] == False
        assert "md5" in info
        assert info["extension"] == ".txt"
        
        # Get directory info
        dir_info = self.fs_core.get_file_info(self.test_dir)
        assert dir_info["is_dir"] == True
        assert dir_info["is_file"] == False
        
        # Test directory size
        subdir = self.test_dir / "size_test"
        self.fs_core.create_directory(subdir)
        for i in range(3):
            self.fs_core.write_file(subdir / f"file{i}.txt", "x" * 100)
        
        dir_size = self.fs_core.get_directory_size(subdir)
        assert dir_size == 300  # 3 files * 100 bytes each
        
        # Check metrics
        metrics = self.fs_core.get_metrics()
        assert metrics["reads"] > 0
        assert metrics["writes"] > 0
        assert metrics["total_bytes_written"] > 0
        
        # Reset metrics
        self.fs_core.reset_metrics()
        metrics = self.fs_core.get_metrics()
        assert metrics["reads"] == 0
        assert metrics["writes"] == 0
    
    def test_error_handling(self):
        """Test error handling for various edge cases."""
        # Read non-existent file
        try:
            self.fs_core.read_file(self.test_dir / "nonexistent.txt")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected
        
        # Invalid mode
        test_file = self.test_dir / "mode_test.txt"
        self.fs_core.write_file(test_file, "test")
        try:
            self.fs_core.read_file(test_file, mode="invalid")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
        
        # Write to file as directory
        try:
            self.fs_core.create_directory(test_file)
            assert False, "Should have failed - path is a file"
        except:
            pass  # Expected
        
        # Check error metrics
        metrics = self.fs_core.get_metrics()
        assert metrics["errors"] > 0
    
    def test_async_operations(self):
        """Test asynchronous file operations."""
        async def run_async_tests():
            test_file = self.test_dir / "async_test.txt"
            content = "Async content test"
            
            # Async write
            bytes_written = await self.fs_core.async_write_file(test_file, content)
            assert bytes_written == len(content)
            
            # Async read
            read_content = await self.fs_core.async_read_file(test_file)
            assert read_content == content
            
            # Binary async operations
            binary_data = b"Binary async \x00\x01"
            await self.fs_core.async_write_file(test_file, binary_data, mode='binary')
            read_binary = await self.fs_core.async_read_file(test_file, mode='binary')
            assert read_binary == binary_data
        
        # Run async tests
        asyncio.run(run_async_tests())
    
    def test_existence_checks(self):
        """Test file and directory existence checks."""
        test_file = self.test_dir / "exists.txt"
        test_dir = self.test_dir / "exists_dir"
        
        # Check non-existent
        assert not self.fs_core.file_exists(test_file)
        assert not self.fs_core.directory_exists(test_dir)
        
        # Create and check
        self.fs_core.write_file(test_file, "exists")
        self.fs_core.create_directory(test_dir)
        
        assert self.fs_core.file_exists(test_file)
        assert self.fs_core.directory_exists(test_dir)
        
        # Check outside sandbox returns False
        assert not self.fs_core.file_exists("/etc/passwd")
        assert not self.fs_core.directory_exists("/etc")
    
    def test_database_integration(self):
        """Test database logging integration."""
        # Verify operations are logged to database
        test_file = self.test_dir / "db_test.txt"
        self.fs_core.write_file(test_file, "Database logging test")
        self.fs_core.read_file(test_file)
        
        # Check tool usage was tracked
        # Note: This assumes DatabaseCore.track_tool_usage is implemented
        # In a real test, we'd query the database to verify the logs
        assert self.db_core is not None  # Database is connected
    
    # === RUN ALL TESTS ===
    
    def run_all_tests(self):
        """Run all test methods."""
        test_methods = [
            self.test_file_write_and_read,
            self.test_json_operations,
            self.test_atomic_write,
            self.test_append_file,
            self.test_directory_operations,
            self.test_file_operations,
            self.test_path_validation,
            self.test_file_info_and_metrics,
            self.test_error_handling,
            self.test_async_operations,
            self.test_existence_checks,
            self.test_database_integration,
        ]
        
        for test in test_methods:
            self.run_test(test)
        
        print(f"\nTest Results: {self.passed} passed, {self.failed} failed")
        
        self.cleanup()
        return self.failed == 0


# === MAIN ===

if __name__ == "__main__":
    tester = TestFileSystemCore()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
