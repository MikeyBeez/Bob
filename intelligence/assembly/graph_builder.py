"""
graph_builder.py - Graph context traversal module

Handles relationship traversal and graph-based context discovery.
Follows connections between memories, notes, and entities to build
rich contextual understanding. Clean API with configurable traversal.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import math


class RelationshipType(Enum):
    """Types of relationships in the context graph."""
    REFERENCES = "references"
    SIMILAR_TO = "similar_to"
    PART_OF = "part_of"
    FOLLOWS = "follows"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    DERIVED_FROM = "derived_from"
    CUSTOM = "custom"


class TraversalStrategy(Enum):
    """Graph traversal strategies."""
    BREADTH_FIRST = "breadth_first"
    DEPTH_FIRST = "depth_first"
    RELEVANCE_WEIGHTED = "relevance_weighted"
    SHORTEST_PATH = "shortest_path"


@dataclass
class GraphNode:
    """Represents a node in the context graph."""
    node_id: str
    content: Any
    node_type: str
    metadata: Dict[str, Any]
    relevance_score: float = 0.0
    distance_from_source: int = 0
    
    def __hash__(self):
        return hash(self.node_id)
    
    def __eq__(self, other):
        return isinstance(other, GraphNode) and self.node_id == other.node_id


@dataclass
class GraphEdge:
    """Represents a relationship edge in the context graph."""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    weight: float
    metadata: Dict[str, Any]
    created_at: Optional[datetime] = None


class GraphContextBuilder:
    """
    Graph-based context discovery system.
    
    Public API for traversing relationships and discovering
    contextually relevant information through graph analysis.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Traversal configuration
        self.max_depth = self.config.get('max_depth', 3)
        self.max_nodes = self.config.get('max_nodes', 100)
        self.min_relevance = self.config.get('min_relevance_threshold', 0.1)
        self.strategy = TraversalStrategy(self.config.get('strategy', 'relevance_weighted'))
        
        # Relationship weights
        self.relationship_weights = {
            RelationshipType.REFERENCES: self.config.get('references_weight', 0.8),
            RelationshipType.SIMILAR_TO: self.config.get('similar_to_weight', 0.7),
            RelationshipType.PART_OF: self.config.get('part_of_weight', 0.6),
            RelationshipType.FOLLOWS: self.config.get('follows_weight', 0.5),
            RelationshipType.SUPPORTS: self.config.get('supports_weight', 0.9),
            RelationshipType.CONTRADICTS: self.config.get('contradicts_weight', 0.4),
            RelationshipType.DERIVED_FROM: self.config.get('derived_from_weight', 0.6),
            RelationshipType.CUSTOM: self.config.get('custom_weight', 0.5)
        }
        
        # Metrics
        self._metrics = {
            'traversals_performed': 0,
            'nodes_discovered': 0,
            'edges_traversed': 0,
            'max_depth_reached': 0,
            'pruned_nodes': 0
        }
    
    def build_context_graph(self, seed_nodes: List[Any], 
                           relationship_source: Any) -> Dict[str, Any]:
        """
        Main API for building context graph from seed nodes.
        
        Args:
            seed_nodes: Starting points for traversal
            relationship_source: Source for relationship data (database, etc.)
            
        Returns:
            Dict containing discovered nodes, edges, and metadata
        """
        # Convert seed nodes to GraphNode objects
        graph_nodes = {}
        for node in seed_nodes:
            graph_node = self._create_graph_node(node, relevance_score=1.0)
            graph_nodes[graph_node.node_id] = graph_node
        
        # Traverse graph based on strategy
        discovered_nodes, edges = self._traverse_graph(
            list(graph_nodes.keys()),
            relationship_source,
            graph_nodes
        )
        
        # Calculate final relevance scores
        self._calculate_graph_relevance(discovered_nodes, edges)
        
        # Filter by relevance threshold
        filtered_nodes = {
            node_id: node for node_id, node in discovered_nodes.items()
            if node.relevance_score >= self.min_relevance
        }
        
        self._metrics['traversals_performed'] += 1
        self._metrics['nodes_discovered'] += len(filtered_nodes)
        self._metrics['edges_traversed'] += len(edges)
        
        return {
            'nodes': filtered_nodes,
            'edges': edges,
            'seed_nodes': list(graph_nodes.keys()),
            'metadata': {
                'traversal_strategy': self.strategy.value,
                'max_depth_reached': max((node.distance_from_source for node in filtered_nodes.values()), default=0),
                'total_nodes': len(filtered_nodes),
                'total_edges': len(edges),
                'average_relevance': sum(node.relevance_score for node in filtered_nodes.values()) / max(1, len(filtered_nodes))
            }
        }
    
    def find_paths(self, source_id: str, target_id: str, 
                   relationship_source: Any, max_paths: int = 5) -> List[List[str]]:
        """
        Find paths between two nodes in the graph.
        
        Args:
            source_id: Starting node ID
            target_id: Target node ID
            relationship_source: Source for relationship data
            max_paths: Maximum paths to return
            
        Returns:
            List of paths (each path is list of node IDs)
        """
        paths = []
        visited = set()
        
        def find_paths_recursive(current_id: str, target_id: str, 
                                current_path: List[str], depth: int):
            if depth > self.max_depth or len(paths) >= max_paths:
                return
            
            if current_id == target_id:
                paths.append(current_path + [current_id])
                return
            
            if current_id in visited:
                return
            
            visited.add(current_id)
            
            # Get relationships for current node
            relationships = self._get_node_relationships(current_id, relationship_source)
            
            for edge in relationships:
                next_id = edge.target_id if edge.source_id == current_id else edge.source_id
                if next_id not in current_path:  # Avoid cycles
                    find_paths_recursive(
                        next_id, target_id, current_path + [current_id], depth + 1
                    )
            
            visited.remove(current_id)
        
        find_paths_recursive(source_id, target_id, [], 0)
        
        return paths
    
    def get_node_neighborhood(self, node_id: str, relationship_source: Any,
                             radius: int = 1) -> Dict[str, Any]:
        """
        Get immediate neighborhood of a node.
        
        Args:
            node_id: Target node ID
            relationship_source: Source for relationship data
            radius: Neighborhood radius (1 = immediate neighbors)
            
        Returns:
            Dict containing neighborhood nodes and edges
        """
        neighborhood_nodes = {}
        neighborhood_edges = []
        
        # Start with the target node
        queue = [(node_id, 0)]
        visited = set()
        
        while queue:
            current_id, distance = queue.pop(0)
            
            if distance > radius or current_id in visited:
                continue
            
            visited.add(current_id)
            
            # Get node data
            node_data = self._get_node_data(current_id, relationship_source)
            if node_data:
                graph_node = self._create_graph_node(
                    node_data, 
                    relevance_score=1.0 - (distance / (radius + 1))
                )
                graph_node.distance_from_source = distance
                neighborhood_nodes[current_id] = graph_node
            
            # Get relationships
            relationships = self._get_node_relationships(current_id, relationship_source)
            
            for edge in relationships:
                neighborhood_edges.append(edge)
                
                # Add connected nodes to queue
                next_id = edge.target_id if edge.source_id == current_id else edge.source_id
                if next_id not in visited and distance < radius:
                    queue.append((next_id, distance + 1))
        
        return {
            'nodes': neighborhood_nodes,
            'edges': neighborhood_edges,
            'center_node': node_id,
            'radius': radius
        }
    
    def _traverse_graph(self, seed_node_ids: List[str], relationship_source: Any,
                       initial_nodes: Dict[str, GraphNode]) -> Tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Traverse graph using configured strategy."""
        if self.strategy == TraversalStrategy.BREADTH_FIRST:
            return self._traverse_breadth_first(seed_node_ids, relationship_source, initial_nodes)
        elif self.strategy == TraversalStrategy.DEPTH_FIRST:
            return self._traverse_depth_first(seed_node_ids, relationship_source, initial_nodes)
        elif self.strategy == TraversalStrategy.RELEVANCE_WEIGHTED:
            return self._traverse_relevance_weighted(seed_node_ids, relationship_source, initial_nodes)
        else:  # SHORTEST_PATH
            return self._traverse_shortest_path(seed_node_ids, relationship_source, initial_nodes)
    
    def _traverse_relevance_weighted(self, seed_node_ids: List[str], 
                                   relationship_source: Any,
                                   nodes: Dict[str, GraphNode]) -> Tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Traverse graph prioritizing high-relevance paths."""
        edges = []
        
        # Priority queue: (negative_relevance, depth, node_id)
        queue = [(-1.0, 0, node_id) for node_id in seed_node_ids]
        visited = set()
        
        while queue and len(nodes) < self.max_nodes:
            queue.sort()  # Sort by relevance (negative, so highest first)
            neg_relevance, depth, current_id = queue.pop(0)
            
            if current_id in visited or depth > self.max_depth:
                continue
            
            visited.add(current_id)
            current_relevance = -neg_relevance
            
            # Get relationships for current node
            relationships = self._get_node_relationships(current_id, relationship_source)
            
            for edge in relationships:
                edges.append(edge)
                
                # Determine next node
                next_id = edge.target_id if edge.source_id == current_id else edge.source_id
                
                if next_id not in nodes and next_id not in visited:
                    # Get node data and calculate relevance
                    node_data = self._get_node_data(next_id, relationship_source)
                    if node_data:
                        # Calculate inherited relevance
                        edge_weight = self.relationship_weights.get(edge.relationship_type, 0.5)
                        inherited_relevance = current_relevance * edge_weight * 0.8  # Decay factor
                        
                        graph_node = self._create_graph_node(node_data, inherited_relevance)
                        graph_node.distance_from_source = depth + 1
                        nodes[next_id] = graph_node
                        
                        # Add to queue if above threshold
                        if inherited_relevance >= self.min_relevance:
                            queue.append((-inherited_relevance, depth + 1, next_id))
        
        return nodes, edges
    
    def _traverse_breadth_first(self, seed_node_ids: List[str],
                               relationship_source: Any,
                               nodes: Dict[str, GraphNode]) -> Tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Standard breadth-first traversal."""
        edges = []
        queue = [(node_id, 0) for node_id in seed_node_ids]
        visited = set()
        
        while queue and len(nodes) < self.max_nodes:
            current_id, depth = queue.pop(0)
            
            if current_id in visited or depth > self.max_depth:
                continue
            
            visited.add(current_id)
            
            relationships = self._get_node_relationships(current_id, relationship_source)
            
            for edge in relationships:
                edges.append(edge)
                next_id = edge.target_id if edge.source_id == current_id else edge.source_id
                
                if next_id not in nodes and next_id not in visited:
                    node_data = self._get_node_data(next_id, relationship_source)
                    if node_data:
                        graph_node = self._create_graph_node(node_data)
                        graph_node.distance_from_source = depth + 1
                        nodes[next_id] = graph_node
                        queue.append((next_id, depth + 1))
        
        return nodes, edges
    
    def _traverse_depth_first(self, seed_node_ids: List[str],
                             relationship_source: Any,
                             nodes: Dict[str, GraphNode]) -> Tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Standard depth-first traversal."""
        edges = []
        visited = set()
        
        def dfs_recursive(node_id: str, depth: int):
            if node_id in visited or depth > self.max_depth or len(nodes) >= self.max_nodes:
                return
            
            visited.add(node_id)
            relationships = self._get_node_relationships(node_id, relationship_source)
            
            for edge in relationships:
                edges.append(edge)
                next_id = edge.target_id if edge.source_id == node_id else edge.source_id
                
                if next_id not in nodes and next_id not in visited:
                    node_data = self._get_node_data(next_id, relationship_source)
                    if node_data:
                        graph_node = self._create_graph_node(node_data)
                        graph_node.distance_from_source = depth + 1
                        nodes[next_id] = graph_node
                        dfs_recursive(next_id, depth + 1)
        
        for seed_id in seed_node_ids:
            dfs_recursive(seed_id, 0)
        
        return nodes, edges
    
    def _traverse_shortest_path(self, seed_node_ids: List[str],
                               relationship_source: Any,
                               nodes: Dict[str, GraphNode]) -> Tuple[Dict[str, GraphNode], List[GraphEdge]]:
        """Traverse focusing on shortest paths between seed nodes."""
        edges = []
        
        # Find shortest paths between all pairs of seed nodes
        for i, source_id in enumerate(seed_node_ids):
            for target_id in seed_node_ids[i+1:]:
                paths = self.find_paths(source_id, target_id, relationship_source, max_paths=3)
                
                for path in paths:
                    for j in range(len(path) - 1):
                        current_id, next_id = path[j], path[j+1]
                        
                        # Add nodes if not present
                        for node_id in [current_id, next_id]:
                            if node_id not in nodes:
                                node_data = self._get_node_data(node_id, relationship_source)
                                if node_data:
                                    graph_node = self._create_graph_node(node_data)
                                    nodes[node_id] = graph_node
                        
                        # Add edge
                        edge_data = self._get_edge_data(current_id, next_id, relationship_source)
                        if edge_data:
                            edges.append(edge_data)
        
        return nodes, edges
    
    def _create_graph_node(self, node_data: Any, relevance_score: float = 0.5) -> GraphNode:
        """Create GraphNode from raw data."""
        node_id = str(getattr(node_data, 'id', hash(str(node_data))))
        node_type = getattr(node_data, 'type', 'unknown')
        metadata = getattr(node_data, 'metadata', {})
        
        return GraphNode(
            node_id=node_id,
            content=node_data,
            node_type=node_type,
            metadata=metadata,
            relevance_score=relevance_score
        )
    
    def _get_node_relationships(self, node_id: str, relationship_source: Any) -> List[GraphEdge]:
        """Get relationships for a node from the relationship source."""
        # This would be implemented based on the actual relationship source
        # For now, return empty list as placeholder
        return []
    
    def _get_node_data(self, node_id: str, relationship_source: Any) -> Any:
        """Get node data from source."""
        # This would be implemented based on the actual data source
        return None
    
    def _get_edge_data(self, source_id: str, target_id: str, relationship_source: Any) -> Optional[GraphEdge]:
        """Get edge data between two nodes."""
        # This would be implemented based on the actual relationship source
        return None
    
    def _calculate_graph_relevance(self, nodes: Dict[str, GraphNode], edges: List[GraphEdge]):
        """Calculate final relevance scores using graph algorithms."""
        # Simple PageRank-like algorithm
        damping = 0.85
        iterations = 10
        
        # Initialize scores
        for node in nodes.values():
            if node.distance_from_source == 0:  # Seed nodes
                node.relevance_score = 1.0
            else:
                node.relevance_score = 0.1
        
        # Iterate to convergence
        for _ in range(iterations):
            new_scores = {}
            
            for node_id, node in nodes.items():
                incoming_score = 0.0
                incoming_edges = [e for e in edges if e.target_id == node_id]
                
                for edge in incoming_edges:
                    source_node = nodes.get(edge.source_id)
                    if source_node:
                        edge_weight = self.relationship_weights.get(edge.relationship_type, 0.5)
                        outgoing_count = len([e for e in edges if e.source_id == edge.source_id])
                        contribution = source_node.relevance_score * edge_weight / max(1, outgoing_count)
                        incoming_score += contribution
                
                new_scores[node_id] = (1 - damping) / len(nodes) + damping * incoming_score
            
            # Update scores
            for node_id, score in new_scores.items():
                nodes[node_id].relevance_score = score
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get graph traversal metrics."""
        return {
            **self._metrics,
            'relationship_weights': {rt.value: weight for rt, weight in self.relationship_weights.items()},
            'traversal_config': {
                'max_depth': self.max_depth,
                'max_nodes': self.max_nodes,
                'min_relevance': self.min_relevance,
                'strategy': self.strategy.value
            }
        }
