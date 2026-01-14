"""Fault Tolerance Manager - Handles crash, omission, and Byzantine failures"""
import time
import threading
import logging
from typing import Dict, List, Optional, Set
from enum import Enum

logger = logging.getLogger(__name__)

class FailureType(Enum):
    CRASH = "crash"
    OMISSION = "omission"
    BYZANTINE = "byzantine"

class NodeStatus:
    """Represents a node's status"""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.healthy = True
        self.last_heartbeat = time.time()
        self.failure_type: Optional[FailureType] = None
        self.failure_count = 0
        self.recovery_time: Optional[float] = None

class FaultManager:
    """Manages fault detection and recovery"""
    
    def __init__(self, config: Dict, node_id: str):
        self.node_id = node_id
        self.heartbeat_interval = config.get('heartbeat_interval', 3)
        self.timeout_threshold = config.get('timeout_threshold', 10)
        self.byzantine_detection = config.get('byzantine_detection', True)
        
        # Track other nodes
        self.node_statuses: Dict[str, NodeStatus] = {}
        
        # Replication groups
        self.replication_groups: Dict[str, List[str]] = {}
        
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        
        logger.info(f"Fault manager initialized for node {node_id}")
    
    def start(self):
        """Start fault monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_nodes, daemon=True)
        self.monitor_thread.start()
        logger.info("Fault monitoring started")
    
    def stop(self):
        """Stop fault monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("Fault monitoring stopped")
    
    def register_node(self, node_id: str, node_type: str):
        """Register a node to monitor"""
        with self.lock:
            if node_id not in self.node_statuses:
                self.node_statuses[node_id] = NodeStatus(node_id)
                logger.info(f"Registered node {node_id} ({node_type}) for monitoring")
    
    def record_heartbeat(self, node_id: str):
        """Record a heartbeat from a node"""
        with self.lock:
            if node_id in self.node_statuses:
                status = self.node_statuses[node_id]
                status.last_heartbeat = time.time()
                
                # Mark as recovered if was failed
                if not status.healthy:
                    logger.info(f"Node {node_id} recovered from failure")
                    status.healthy = True
                    status.failure_type = None
                    status.recovery_time = time.time()
    
    def detect_crash_failure(self, node_id: str) -> bool:
        """Detect crash failure (no response)"""
        with self.lock:
            if node_id not in self.node_statuses:
                return False
            
            status = self.node_statuses[node_id]
            time_since_heartbeat = time.time() - status.last_heartbeat
            
            if time_since_heartbeat > self.timeout_threshold:
                if status.healthy:
                    logger.warning(f"Crash failure detected for node {node_id}")
                    status.healthy = False
                    status.failure_type = FailureType.CRASH
                    status.failure_count += 1
                return True
        
        return False
    
    def detect_omission_failure(self, node_id: str, expected_messages: int, received_messages: int) -> bool:
        """Detect omission failure (missing messages)"""
        if received_messages < expected_messages * 0.8:  # More than 20% missing
            with self.lock:
                if node_id in self.node_statuses:
                    status = self.node_statuses[node_id]
                    if status.healthy:
                        logger.warning(f"Omission failure detected for node {node_id}")
                        status.healthy = False
                        status.failure_type = FailureType.OMISSION
                        status.failure_count += 1
                    return True
        return False
    
    """def detect_byzantine_failure(self, node_id: str, inconsistent_responses: List[Dict]) -> bool:
        ""Detect Byzantine failure (inconsistent behavior)"""
        if not self.byzantine_detection:
            return False
        
        # Simple Byzantine detection: check for inconsistent responses
        if len(set(str(r) for r in inconsistent_responses)) > len(inconsistent_responses) * 0.3:
            with self.lock:
                if node_id in self.node_statuses:
                    status = self.node_statuses[node_id]
                    if status.healthy:
                        logger.warning(f"Byzantine failure detected for node {node_id}")
                        status.healthy = False
                        status.failure_type = FailureType.BYZANTINE
                        status.failure_count += 1
                    return True
        return False"""
    
    def detect_byzantine_failure(self, node_id: str, responses: List[Dict]) -> bool:
    """Implement majority voting to detect Byzantine actors """
    if not self.byzantine_detection or len(responses) < 2:
        return False
    
    # Check if any response deviates from the majority
    fingerprints = [str(sorted(r.items())) for r in responses]
    most_common = max(set(fingerprints), key=fingerprints.count)
    
    if fingerprints.count(most_common) < (len(responses) / 2 + 1):
        logger.error(f"Byzantine inconsistency detected at node {node_id}") [cite: 137]
        return True
    return False

     def get_failed_nodes(self) -> List[str]:
        """Get list of failed nodes"""
        with self.lock:
            return [node_id for node_id, status in self.node_statuses.items() if not status.healthy]
    
    def get_node_status(self, node_id: str) -> Optional[Dict]:
        """Get status of a specific node"""
        with self.lock:
            if node_id not in self.node_statuses:
                return None
            
            status = self.node_statuses[node_id]
            return {
                'node_id': node_id,
                'healthy': status.healthy,
                'failure_type': status.failure_type.value if status.failure_type else None,
                'failure_count': status.failure_count,
                'last_heartbeat': status.last_heartbeat,
                'time_since_heartbeat': time.time() - status.last_heartbeat
            }
    
    def _monitor_nodes(self):
        """Monitor nodes for failures"""
        while self.running:
            try:
                with self.lock:
                    nodes_to_check = list(self.node_statuses.keys())
                
                for node_id in nodes_to_check:
                    self.detect_crash_failure(node_id)
                
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in fault monitoring: {e}", exc_info=True)
                time.sleep(self.heartbeat_interval)
    
    def get_status(self) -> Dict:
        """Get overall fault tolerance status"""
        with self.lock:
            total_nodes = len(self.node_statuses)
            healthy_nodes = sum(1 for s in self.node_statuses.values() if s.healthy)
            failed_nodes = self.get_failed_nodes()
            
            return {
                'total_nodes': total_nodes,
                'healthy_nodes': healthy_nodes,
                'failed_nodes': len(failed_nodes),
                'failed_node_ids': failed_nodes,
                'availability': (healthy_nodes / total_nodes * 100) if total_nodes > 0 else 0
            }
