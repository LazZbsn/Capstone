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
import requests

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.common.utils import load_config, get_system_metrics, setup_logging, calculate_latency
from src.common.metrics import MetricsCollector

setup_logging()
logger = logging.getLogger(__name__)

class EdgeNode:
    """Edge node implementation for low-latency request handling"""
    
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.node_id = self.config['node_id']
        self.host = self.config['host']
        self.port = self.config['port']
        
        # Initialize cache (Requirement 2 & 4: Optimize latency)
        self.cache = redis.Redis(
            host='localhost',
            port=self.config.get('cache_port', 6379),
            decode_responses=True
        )
        
        self.current_core_index = 0
        self.metrics = MetricsCollector('edge', self.config['metrics']['port'])
        
        # Flask app for HTTP API
        self.app = Flask(__name__)
        self.app.route('/api/request', methods=['POST'])(self.handle_request)
        self.app.route('/api/metrics', methods=['GET'])(self.get_metrics)
        self.app.route('/api/health', methods=['GET'])(self.health_check)
        
        self.running = True
        self.load_report_thread = None
        logger.info(f"Edge node {self.node_id} initialized")
    
    def start(self):
        """Start the edge node and reporting threads"""
        self.load_report_thread = threading.Thread(target=self._report_load, daemon=True)
        self.load_report_thread.start()
        self.app.run(host=self.host, port=self.port, threaded=True)
    
    def handle_request(self):
        """Handle incoming HTTP request with Caching logic"""
        start_time = time.time()
        try:
            data = request.json
            request_id = data.get('request_id', f"req-{int(time.time() * 1000)}")
            operation = data.get('operation', 'unknown')
            
            # Check cache (Task 4: Optimize network resources)
            cache_key = f"{operation}:{json.dumps(data.get('data', {}), sort_keys=True)}"
            cached_response = self.cache.get(cache_key)
            
            if cached_response:
                latency = calculate_latency(start_time)
                self.metrics.record_request(operation, True, latency)
                return jsonify({
                    'request_id': request_id,
                    'success': True,
                    'data': json.loads(cached_response),
                    'from_cache': True,
                    'latency_ms': latency
                }), 200
            
            # Cache miss - forward to core
            response_data = self._forward_to_core(operation, data)
            
            if response_data.get('success'):
                self.cache.setex(cache_key, 300, json.dumps(response_data.get('data', {})))
            
            latency = calculate_latency(start_time)
            self.metrics.record_request(operation, response_data.get('success', False), latency)
            return jsonify(response_data), 200
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

    def _get_core_node(self):
        """Round-robin core node selection"""
        nodes = self.config.get('core_nodes', [])
        if not nodes: return None
        node = nodes[self.current_core_index]
        self.current_core_index = (self.current_core_index + 1) % len(nodes)
        return node

    def _forward_to_core(self, operation: str, data: Dict) -> Dict:
        """Requirement: Integration of edge-core-cloud integration"""
        core = self._get_core_node()
        if not core: return {"success": False, "error": "No core nodes available"}
        
        url = f"http://{core['host']}:{core['port']}/api/transaction"
        payload = {
            "transaction_id": f"txn-{int(time.time()*1000)}",
            "operations": [{"operation_type": "write", "parameters": data}]
        }
        try:
            resp = requests.post(url, json=payload, timeout=5)
            return resp.json()
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _report_load(self):
        """Task 1: Periodic load reporting for dynamic optimization"""
        while self.running:
            try:
                metrics = get_system_metrics()
                logger.debug(f"Node {self.node_id} load: {metrics['cpu_percent']}%")
                time.sleep(self.config.get('load_balancer', {}).get('health_check_interval', 5))
            except Exception as e:
                time.sleep(5)

    def get_metrics(self):
        return jsonify({'node_id': self.node_id, 'system': get_system_metrics()}), 200

    def health_check(self):
        return jsonify({'status': 'healthy', 'node_id': self.node_id}), 200

    def stop(self):
        self.running = False

if __name__ == '__main__':
    node = EdgeNode(sys.argv[1] if len(sys.argv) > 1 else 'config/edge_config.json')
    node.start()
