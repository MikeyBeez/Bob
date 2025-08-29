"""
test_context_assembler.py - Comprehensive test suite serving as API documentation

This test suite serves dual purposes:
1. Validates the complete context assembly system integration
2. Acts as comprehensive API documentation showing usage patterns

The tests demonstrate the full modular architecture with all 6 submodules:
- SourceManager: Multi-source context management  
- ContextPrioritizer: Intelligent relevance scoring with temporal decay
- ContextFormatter: LLM-optimized output with token management
- CacheManager: Intelligent caching with TTL strategies
- GraphContextBuilder: Relationship traversal and graph analysis
- AssemblyMetrics: Performance and usage analytics

Each test method documents a specific use case and validates the expected behavior.
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Import the main ContextAssembler and all submodule components
from intelligence.context_assembler import ContextAssembler
from intelligence.assembly import (
    SourceManager, ContextSource, SourceType, SourceStatus,
    ContextPrioritizer, ContextItem,
    ContextFormatter, FormatType, FormattedSection,
    CacheManager, CacheStrategy,
    GraphContextBuilder, TraversalStrategy,
    AssemblyMetrics, MetricType
)


class TestContextAssemblerAPI:
    """
    Test suite for the main ContextAssembler API.
    
    These tests validate the clean API interface and demonstrate proper usage
    patterns for the complete context assembly system.
    """
    
    @pytest.fixture
    def mock_db_core(self):
        """Mock DatabaseCore for testing."""
        db_mock = Mock()
        db_mock.search_memories = AsyncMock(return_value=[
            {'content': 'Database memory 1', 'relevance': 0.9},
            {'content': 'Database memory 2', 'relevance': 0.7}
        ])
        return db_mock
    
    @pytest.fixture
    def mock_fs_core(self):
        """Mock FileSystemCore for testing."""
        fs_mock = Mock()
        fs_mock.search_files = AsyncMock(return_value=[
            {'path': '/test/file1.txt', 'content': 'File content 1'},
            {'path': '/test/file2.txt', 'content': 'File content 2'}
        ])
        return fs_mock
    
    @pytest.fixture
    def context_assembler(self, mock_db_core, mock_fs_core):
        """Create ContextAssembler instance for testing."""
        return ContextAssembler(
            db_core=mock_db_core,
            fs_core=mock_fs_core,
            max_context_size=8000,
            cache_ttl=300
        )
    
    @pytest.mark.asyncio
    async def test_basic_context_assembly(self, context_assembler):
        """
        Test basic context assembly workflow.
        
        This demonstrates the primary use case:
        1. Provide a query
        2. Get formatted context optimized for LLM consumption
        3. Receive metadata about the assembly process
        """
        query = "How to implement user authentication?"
        
        result = await context_assembler.assemble_context(query)
        
        # Validate result structure
        assert isinstance(result, dict)
        assert 'formatted_context' in result
        assert 'metadata' in result
        assert 'sections' in result
        assert 'raw_items_count' in result
        assert 'prioritized_items_count' in result
        
        # Validate metadata
        metadata = result['metadata']
        assert metadata['query'] == query
        assert 'assembly_time_ms' in metadata
        assert 'sources_used' in metadata
        assert 'session_id' in metadata
        
        # Validate formatted context is string
        assert isinstance(result['formatted_context'], str)
        assert len(result['formatted_context']) > 0
    
    @pytest.mark.asyncio 
    async def test_context_assembly_with_token_limits(self, context_assembler):
        """
        Test context assembly with custom token limits.
        
        This demonstrates token-aware formatting to respect LLM context windows.
        """
        query = "Explain machine learning concepts"
        max_tokens = 4000
        
        result = await context_assembler.assemble_context(
            query, 
            max_tokens=max_tokens
        )
        
        # Should respect token limits
        assert result['metadata']['total_tokens'] <= max_tokens
        assert len(result['formatted_context']) > 0
    
    @pytest.mark.asyncio
    async def test_context_assembly_with_specific_sources(self, context_assembler):
        """
        Test context assembly using only specific sources.
        
        This demonstrates selective source usage for focused context.
        """
        query = "Database optimization strategies"
        sources = ['default_database']  # Only use database source
        
        result = await context_assembler.assemble_context(
            query,
            sources=sources
        )
        
        # Validate sources were filtered
        sources_used = result['metadata']['sources_used'] 
        if sources_used:  # If any sources returned data
            assert all('database' in source.lower() for source in sources_used)
    
    @pytest.mark.asyncio
    async def test_context_assembly_different_formats(self, context_assembler):
        """
        Test different output format types.
        
        This demonstrates flexible output formatting for different LLM prompting styles.
        """
        query = "Software architecture patterns"
        
        # Test structured prompt format
        structured_result = await context_assembler.assemble_context(
            query,
            format_type=FormatType.STRUCTURED_PROMPT
        )
        
        # Test conversational format
        conversational_result = await context_assembler.assemble_context(
            query,
            format_type=FormatType.CONVERSATIONAL
        )
        
        # Both should produce valid output
        assert len(structured_result['formatted_context']) > 0
        assert len(conversational_result['formatted_context']) > 0
        
        # Formats should be different
        assert structured_result['formatted_context'] != conversational_result['formatted_context']
    
    @pytest.mark.asyncio
    async def test_graph_expansion_toggle(self, context_assembler):
        """
        Test enabling/disabling graph-based context expansion.
        
        This demonstrates relationship traversal for discovering related context.
        """
        query = "Project management methodologies"
        
        # Test with graph expansion enabled
        with_expansion = await context_assembler.assemble_context(
            query,
            enable_graph_expansion=True
        )
        
        # Test with graph expansion disabled
        without_expansion = await context_assembler.assemble_context(
            query,
            enable_graph_expansion=False
        )
        
        # Validate graph expansion flag in metadata
        assert with_expansion['metadata']['graph_expansion_enabled'] == True
        assert without_expansion['metadata']['graph_expansion_enabled'] == False
    
    def test_add_context_source(self, context_assembler):
        """
        Test adding new context sources dynamically.
        
        This demonstrates runtime configuration of context sources.
        """
        # Add a new API source
        success = context_assembler.add_context_source('external_api', {
            'endpoint': 'https://api.example.com/search',
            'priority': 0.7,
            'timeout': 5000
        })
        
        assert success == True
        
        # Adding invalid source type should fail
        failure = context_assembler.add_context_source('invalid_type', {})
        assert failure == False
    
    def test_context_cache_management(self, context_assembler):
        """
        Test context cache operations.
        
        This demonstrates cache management for performance optimization.
        """
        # Clear cache should return count
        cleared_count = context_assembler.clear_context_cache()
        assert isinstance(cleared_count, int)
        assert cleared_count >= 0
        
        # Clear cache with age filter
        cleared_count = context_assembler.clear_context_cache(max_age_seconds=3600)
        assert isinstance(cleared_count, int)
    
    def test_context_priorities_configuration(self, context_assembler):
        """
        Test setting context source priorities.
        
        This demonstrates priority weighting for different context sources.
        """
        priority_config = {
            'database': 0.9,
            'filesystem': 0.6,
            'external_api': 0.4,
            'query_relevance': 0.8
        }
        
        success = context_assembler.set_context_priorities(priority_config)
        assert success == True
        
        # Verify priorities are stored
        assert context_assembler.config['source_priorities']['database'] == 0.9
    
    def test_context_metrics_collection(self, context_assembler):
        """
        Test comprehensive metrics collection.
        
        This demonstrates performance monitoring and usage analytics.
        """
        metrics = context_assembler.get_context_metrics()
        
        # Validate metrics structure
        assert isinstance(metrics, dict)
        assert 'session_id' in metrics
        assert 'configuration' in metrics
        assert 'submodule_metrics' in metrics
        assert 'performance_summary' in metrics
        assert 'quality_trends' in metrics
        assert 'usage_analytics' in metrics
        assert 'generated_at' in metrics
        
        # Validate submodule metrics
        submodule_metrics = metrics['submodule_metrics']
        expected_submodules = [
            'source_manager', 'cache_manager', 'formatter', 
            'prioritizer', 'graph_builder', 'assembly_metrics'
        ]
        
        for submodule in expected_submodules:
            assert submodule in submodule_metrics
    
    @pytest.mark.asyncio
    async def test_error_handling(self, context_assembler):
        """
        Test error handling and graceful degradation.
        
        This demonstrates robust error handling in the context assembly process.
        """
        # Test with invalid query
        result = await context_assembler.assemble_context("")
        assert 'error' not in result['metadata']  # Empty query should be handled gracefully
        
        # Mock a source failure scenario
        context_assembler.source_manager.fetch_from_sources = AsyncMock(
            side_effect=Exception("Source unavailable")
        )
        
        result = await context_assembler.assemble_context("test query")
        
        # Should still return a result, even with errors
        assert isinstance(result, dict)
        assert 'formatted_context' in result


if __name__ == '__main__':
    """
    Run comprehensive test suite.
    
    This serves as both validation and live documentation of the 
    complete context assembly system capabilities.
    """
    pytest.main([
        __file__,
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--durations=10'  # Show 10 slowest tests
    ])
