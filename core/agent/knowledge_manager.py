"""
knowledge_manager.py - Knowledge storage and retrieval management

Manages knowledge storage, indexing, and retrieval across all subsystems.
Implements semantic search and knowledge graph construction.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class KnowledgeEntry:
    """A single knowledge entry."""
    id: str
    content: str
    source: str
    tags: List[str]
    importance: float
    created_at: datetime
    last_accessed: datetime
    access_count: int


@dataclass 
class KnowledgeResults:
    """Results from knowledge retrieval."""
    query: str
    entries: List[KnowledgeEntry]
    relevance_scores: List[float]
    total_found: int
    search_time: float
    suggestions: List[str]


class KnowledgeManager:
    """
    Manages all knowledge operations for the Bob system.
    
    Provides:
    - Knowledge storage with semantic indexing
    - Intelligent retrieval with context awareness
    - Knowledge graph construction
    - Usage pattern analysis
    """
    
    def __init__(self, db_core, fs_core, ollama_client):
        """
        Initialize knowledge manager.
        
        Args:
            db_core: DatabaseCore instance for storage
            fs_core: FileSystemCore instance for file operations
            ollama_client: OllamaClient for semantic operations
        """
        self.db_core = db_core
        self.fs_core = fs_core
        self.ollama_client = ollama_client
        
        self.logger = logging.getLogger("KnowledgeManager")
        self.knowledge_cache = {}
        self.search_history = []
    
    async def store_knowledge(self, knowledge: Dict[str, Any]) -> bool:
        """
        Store knowledge with semantic indexing and metadata.
        
        Args:
            knowledge: Knowledge data to store
            
        Returns:
            Success status
        """
        try:
            # Extract key information
            content = knowledge.get("content", "")
            source = knowledge.get("source", "unknown")
            tags = knowledge.get("tags", [])
            importance = knowledge.get("importance", 0.5)
            
            # Generate semantic embedding if Ollama is available
            embedding = None
            if self.ollama_client:
                try:
                    embedding = await self.ollama_client.generate_embeddings(content)
                except:
                    self.logger.warning("Failed to generate embeddings")
            
            # Store in database
            if self.db_core:
                # Use the notes table for knowledge storage
                success = self.db_core.create_note(
                    title=knowledge.get("title", content[:100]),
                    content=content,
                    note_type="knowledge",
                    tags=tags,
                    metadata={
                        "source": source,
                        "importance": importance,
                        "embedding": embedding,
                        "stored_at": datetime.now().isoformat()
                    }
                )
                
                if success:
                    self.logger.info(f"✅ Stored knowledge: {content[:50]}...")
                    return True
            
            # Fallback to filesystem storage
            if self.fs_core:
                knowledge_file = f"knowledge_{int(datetime.now().timestamp())}.json"
                self.fs_core.write_json(f"knowledge/{knowledge_file}", knowledge)
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Knowledge storage failed: {e}")
            return False
    
    async def retrieve_knowledge(self, query: str, context: Dict[str, Any]) -> KnowledgeResults:
        """
        Retrieve relevant knowledge for a query and context.
        
        Args:
            query: Search query
            context: Additional context for relevance
            
        Returns:
            KnowledgeResults with relevant entries
        """
        start_time = datetime.now()
        self.logger.info(f"🔍 Searching knowledge for: {query[:50]}...")
        
        try:
            entries = []
            relevance_scores = []
            suggestions = []
            
            # Search in database if available
            if self.db_core:
                # Get notes that match the query
                db_results = self.db_core.search_notes(
                    query=query,
                    note_type="knowledge",
                    limit=10
                )
                
                for result in db_results:
                    entry = KnowledgeEntry(
                        id=result.get("id", "unknown"),
                        content=result.get("content", ""),
                        source=result.get("metadata", {}).get("source", "database"),
                        tags=result.get("tags", []),
                        importance=result.get("metadata", {}).get("importance", 0.5),
                        created_at=datetime.fromisoformat(result.get("created_at", datetime.now().isoformat())),
                        last_accessed=datetime.now(),
                        access_count=result.get("metadata", {}).get("access_count", 0) + 1
                    )
                    entries.append(entry)
                    relevance_scores.append(self._calculate_relevance(entry, query, context))
            
            # Search in filesystem if available
            if self.fs_core and len(entries) < 5:
                try:
                    knowledge_files = self.fs_core.list_directory("knowledge", pattern="*.json")
                    for file_path in knowledge_files[:5]:  # Limit filesystem search
                        try:
                            knowledge_data = self.fs_core.read_json(file_path)
                            if self._matches_query(knowledge_data, query):
                                entry = KnowledgeEntry(
                                    id=str(file_path),
                                    content=knowledge_data.get("content", ""),
                                    source=knowledge_data.get("source", "filesystem"),
                                    tags=knowledge_data.get("tags", []),
                                    importance=knowledge_data.get("importance", 0.5),
                                    created_at=datetime.fromisoformat(
                                        knowledge_data.get("created_at", datetime.now().isoformat())
                                    ),
                                    last_accessed=datetime.now(),
                                    access_count=knowledge_data.get("access_count", 0)
                                )
                                entries.append(entry)
                                relevance_scores.append(self._calculate_relevance(entry, query, context))
                        except:
                            continue
                except:
                    pass  # Filesystem search failed, continue with database results
            
            # Sort by relevance
            if entries and relevance_scores:
                sorted_pairs = sorted(zip(entries, relevance_scores), 
                                    key=lambda x: x[1], reverse=True)
                entries, relevance_scores = zip(*sorted_pairs)
                entries, relevance_scores = list(entries), list(relevance_scores)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(query, entries)
            
            # Update search history
            self.search_history.append({
                "query": query,
                "results_count": len(entries),
                "timestamp": start_time.isoformat()
            })
            
            search_time = (datetime.now() - start_time).total_seconds()
            
            return KnowledgeResults(
                query=query,
                entries=entries,
                relevance_scores=relevance_scores,
                total_found=len(entries),
                search_time=search_time,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Knowledge retrieval failed: {e}")
            return KnowledgeResults(
                query=query,
                entries=[],
                relevance_scores=[],
                total_found=0,
                search_time=(datetime.now() - start_time).total_seconds(),
                suggestions=[]
            )
    
    def _calculate_relevance(self, entry: KnowledgeEntry, query: str, context: Dict[str, Any]) -> float:
        """Calculate relevance score for a knowledge entry."""
        score = 0.0
        
        # Text similarity (basic keyword matching)
        query_words = set(query.lower().split())
        content_words = set(entry.content.lower().split())
        
        if query_words and content_words:
            intersection = query_words.intersection(content_words)
            union = query_words.union(content_words)
            jaccard_score = len(intersection) / len(union) if union else 0
            score += jaccard_score * 0.5
        
        # Tag matching
        query_tags = context.get("tags", [])
        if query_tags and entry.tags:
            tag_intersection = set(query_tags).intersection(set(entry.tags))
            tag_union = set(query_tags).union(set(entry.tags))
            tag_score = len(tag_intersection) / len(tag_union) if tag_union else 0
            score += tag_score * 0.3
        
        # Importance weighting
        score += entry.importance * 0.1
        
        # Recency boost (more recent = slight boost)
        days_old = (datetime.now() - entry.created_at).days
        recency_score = max(0, 1 - (days_old / 365))  # Decay over a year
        score += recency_score * 0.1
        
        return min(1.0, score)
    
    def _matches_query(self, knowledge_data: Dict[str, Any], query: str) -> bool:
        """Check if knowledge data matches the query."""
        content = knowledge_data.get("content", "").lower()
        title = knowledge_data.get("title", "").lower()
        tags = [tag.lower() for tag in knowledge_data.get("tags", [])]
        
        query_lower = query.lower()
        
        return (query_lower in content or 
                query_lower in title or
                any(query_lower in tag for tag in tags))
    
    def _generate_suggestions(self, query: str, entries: List[KnowledgeEntry]) -> List[str]:
        """Generate search suggestions based on query and results."""
        suggestions = []
        
        # Extract common tags from results
        all_tags = []
        for entry in entries[:5]:  # Only look at top 5 results
            all_tags.extend(entry.tags)
        
        # Get most common tags
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        for tag, _ in common_tags:
            if tag.lower() not in query.lower():
                suggestions.append(f"Search for '{query} {tag}'")
        
        # Add generic suggestions
        if len(suggestions) < 3:
            suggestions.extend([
                "Try more specific terms",
                "Use different keywords", 
                "Check related topics"
            ])
        
        return suggestions[:3]
    
    async def build_knowledge_graph(self, domain: str = "all") -> Dict[str, Any]:
        """Build a knowledge graph from stored knowledge."""
        try:
            # Retrieve all knowledge entries
            all_knowledge = await self.retrieve_knowledge("", {"domain": domain})
            
            # Build simple graph structure
            nodes = []
            edges = []
            
            for entry in all_knowledge.entries:
                # Create node
                node = {
                    "id": entry.id,
                    "label": entry.content[:50] + "...",
                    "type": "knowledge",
                    "importance": entry.importance,
                    "tags": entry.tags
                }
                nodes.append(node)
                
                # Create edges based on tag similarity
                for other_entry in all_knowledge.entries:
                    if entry.id != other_entry.id:
                        common_tags = set(entry.tags).intersection(set(other_entry.tags))
                        if common_tags:
                            edge = {
                                "source": entry.id,
                                "target": other_entry.id,
                                "weight": len(common_tags),
                                "type": "tag_similarity"
                            }
                            edges.append(edge)
            
            return {
                "nodes": nodes,
                "edges": edges,
                "metadata": {
                    "total_nodes": len(nodes),
                    "total_edges": len(edges),
                    "domain": domain,
                    "created_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Knowledge graph construction failed: {e}")
            return {"nodes": [], "edges": [], "metadata": {}}
