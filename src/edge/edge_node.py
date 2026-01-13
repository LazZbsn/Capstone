"""Edge Node - Handles user requests with low latency"""
import json
import time
import threading
import logging
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import redis
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.common.utils import load_config, get_system_metrics, setup_logging, calculate_latency
from src.common.metrics import MetricsCollector
from src.common.rpc_client import RPCClient

# Import generated gRPC code (will be generated from proto)
# from src.common.proto import telecom_pb2, telecom_pb2_grpc

setup_logging()
logger = logging.getLogger(__name__)

class EdgeNode:
    """Edge node implementation for low-latency request handling"""
    
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.node_id = self.config['node_id']
        self.host = self.config['host']
        self.port = self.config['port']
        
        # Initialize cache
        self.cache = redis.Redis(
            host='localhost',
            port=self.config.get('cache_port', 6379),
            decode_responses=True
        )
        
        # Core node clients
        self.core_clients = []
        self.current_core_index = 0
        
        # Metrics
        self.metrics = MetricsCollector('edge', self.config['metrics']['port'])
        
        # Flask app for HTTP API
        self.app = Flask(__name__)
        self.app.route('/api/request', methods=['POST'])(self.handle_request)
        self.app.route('/api/metrics', methods=['GET'])(self.get_metrics)
        self.app.route('/api/health', methods=['GET'])(self.health_check)
        
        # Threading
        self.running = True
        self.load_report_thread = None
        
        logger.info(f"Edge node {self.node_id} initialized")
    
    def start(self):
        """Start the edge node"""
        logger.info(f"Starting edge node {self.node_id} on {self.host}:{self.port}")
        
        # Start load reporting thread
        self.load_report_thread = threading.Thread(target=self._report_load, daemon=True)
        self.load_report_thread.start()
        
        # Start Flask server
        self.app.run(host=self.host, port=self.port, threaded=True)
    
    def handle_request(self):
        """Handle incoming HTTP request"""
        start_time = time.time()
        try:
            data = request.json
            request_id = data.get('request_id', f"req-{int(time.time() * 1000)}")
            operation = data.get('operation', 'unknown')
            
            logger.info(f"Received request {request_id}: {operation}")
            
            # Check cache first
            cache_key = f"{operation}:{json.dumps(data.get('data', {}), sort_keys=True)}"
            cached_response = self.cache.get(cache_key)
            
            if cached_response:
                logger.info(f"Cache hit for {request_id}")
                latency = calculate_latency(start_time)
                self.metrics.record_request(operation, True, latency)
                return jsonify({
                    'request_id': request_id,
                    'success': True,
                    'data': json.loads(cached_response),
                    'from_cache': True,
                    'latency_ms': latency
                }), 200
            
            # Cache miss - forward to core node
            core_node = self._get_core_node()
            if not core_node:
                raise Exception("No available core nodes")
            
            # For now, simulate RPC call (will be replaced with actual gRPC)
            response_data = self._forward_to_core(operation, data)
            
            # Cache successful responses
            if response_data.get('success'):
                self.cache.setex(cache_key, 300, json.dumps(response_data.get('data', {})))  # 5 min TTL
            
            latency = calculate_latency(start_time)
            self.metrics.record_request(operation, response_data.get('success', False), latency)
            
            return jsonify({
                'request_id': request_id,
                'success': response_data.get('success', False),
                'data': response_data.get('data', {}),
                'from_cache': False,
                'latency_ms': latency
            }), 200
            
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            latency = calculate_latency(start_time)
            self.metrics.record_request('unknown', False, latency)
            return jsonify({
                'success': False,
                'error': str(e),
                'latency_ms': latency
            }), 500
    
    def _get_core_node(self):
        """Get next core node using round-robin"""
        if not self.config.get('core_nodes'):
            return None
        
        core_config = self.config['core_nodes'][self.current_core_index]
        self.current_core_index = (self.current_core_index + 1) % len(self.config['core_nodes'])
        return core_config
    
    def _forward_to_core(self, operation: str, data: Dict) -> Dict:
        """Forward request to core node (simulated for now)"""
        # TODO: Implement actual gRPC call
        # For now, simulate processing
        time.sleep(0.01)  # Simulate network latency
        
        return {
            'success': True,
            'data': {
                'operation': operation,
                'processed_by': 'core-node',
                'result': 'success'
            }
        }
    
    def get_metrics(self):
        """Get node metrics"""
        system_metrics = get_system_metrics()
        request_metrics = self.metrics.get_metrics()
        
        return jsonify({
            'node_id': self.node_id,
            'node_type': 'edge',
            'system': system_metrics,
            'requests': request_metrics
        }), 200
    
    def health_check(self):
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'node_id': self.node_id,
            'timestamp': time.time()
        }), 200
    
    def _report_load(self):
        """Periodically report load to core nodes"""
        while self.running:
            try:
                metrics = get_system_metrics()
                # TODO: Send heartbeat to core nodes via gRPC
                time.sleep(self.config.get('load_balancer', {}).get('health_check_interval', 5))
            except Exception as e:
                logger.error(f"Error reporting load: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop the edge node"""
        self.running = False
        logger.info(f"Stopping edge node {self.node_id}")

if __name__ == '__main__':
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config/edge_config.json'
    node = EdgeNode(config_path)
    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()
