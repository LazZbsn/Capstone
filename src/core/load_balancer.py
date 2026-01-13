"""Load Balancer for dynamic node selection"""
import time
import logging
from typing import List, Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class LoadBalancer:
    """Load balancer with multiple strategies"""
    
    def __init__(self, edge_nodes: List[Dict], cloud_nodes: List[Dict]):
        self.edge_nodes = edge_nodes
        self.cloud_nodes = cloud_nodes
        
        # Track node metrics
        self.node_metrics = defaultdict(lambda: {
            'cpu': 0.0,
            'memory': 0.0,
            'active_connections': 0,
            'requests_per_second': 0,
            'last_update': time.time(),
            'healthy': True
        })
        
        # Round-robin counters
        self.edge_index = 0
        self.cloud_index = 0
        
        logger.info(f"Load balancer initialized with {len(edge_nodes)} edge nodes, {len(cloud_nodes)} cloud nodes")
    
    def update_node_metrics(self, node_id: str, metrics: Dict):
        """Update metrics for a node"""
        self.node_metrics[node_id].update(metrics)
        self.node_metrics[node_id]['last_update'] = time.time()
    
    def select_node(self, node_type: str = 'edge', strategy: str = 'round_robin') -> Optional[Dict]:
        """Select a node based on strategy"""
        nodes = self.edge_nodes if node_type == 'edge' else self.cloud_nodes
        
        if not nodes:
            return None
        
        # Filter healthy nodes
        healthy_nodes = [
            node for node in nodes
            if self.node_metrics[node.get('node_id', 'unknown')]['healthy']
        ]
        
        if not healthy_nodes:
            healthy_nodes = nodes  # Fallback to all nodes
        
        if strategy == 'round_robin':
            return self._round_robin(healthy_nodes, node_type)
        elif strategy == 'least_connections':
            return self._least_connections(healthy_nodes)
        elif strategy == 'least_cpu':
            return self._least_cpu(healthy_nodes)
        else:
            return self._round_robin(healthy_nodes, node_type)
    
    def _round_robin(self, nodes: List[Dict], node_type: str) -> Dict:
        """Round-robin selection"""
        if node_type == 'edge':
            node = nodes[self.edge_index % len(nodes)]
            self.edge_index += 1
            return node
        else:
            node = nodes[self.cloud_index % len(nodes)]
            self.cloud_index += 1
            return node
    
    def _least_connections(self, nodes: List[Dict]) -> Dict:
        """Select node with least active connections"""
        return min(nodes, key=lambda n: self.node_metrics[n.get('node_id', 'unknown')]['active_connections'])
    
    def _least_cpu(self, nodes: List[Dict]) -> Dict:
        """Select node with lowest CPU usage"""
        return min(nodes, key=lambda n: self.node_metrics[n.get('node_id', 'unknown')]['cpu'])
