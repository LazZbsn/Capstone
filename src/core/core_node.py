"""Core Node - Coordinates transactions and load balancing"""
import json
import time
import threading
import logging
from flask import Flask, request, jsonify
from typing import Dict, Any, List, Optional
from collections import defaultdict
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.common.utils import load_config, get_system_metrics, setup_logging
from src.common.metrics import MetricsCollector
from src.transactions.transaction_manager import TransactionManager
from src.fault_tolerance.fault_manager import FaultManager
from load_balancer import LoadBalancer

setup_logging()
logger = logging.getLogger(__name__)

class CoreNode:
    """Core node implementation for transaction coordination"""
    
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.node_id = self.config['node_id']
        self.host = self.config['host']
        self.port = self.config['port']
        
        # Initialize components
        self.transaction_manager = TransactionManager(self.config.get('transaction', {}))
        self.fault_manager = FaultManager(
            self.config.get('fault_tolerance', {}),
            self.node_id
        )
        self.load_balancer = LoadBalancer(
            self.config.get('edge_nodes', []),
            self.config.get('cloud_nodes', [])
        )
        
        # Metrics
        self.metrics = MetricsCollector('core', self.config['metrics']['port'])
        
        # Flask app
        self.app = Flask(__name__)
        self.app.route('/api/transaction', methods=['POST'])(self.handle_transaction)
        self.app.route('/api/balance', methods=['POST'])(self.handle_load_balance)
        self.app.route('/api/metrics', methods=['GET'])(self.get_metrics)
        self.app.route('/api/health', methods=['GET'])(self.health_check)
        
        self.running = True
        logger.info(f"Core node {self.node_id} initialized")
    
    def start(self):
        """Start the core node"""
        logger.info(f"Starting core node {self.node_id} on {self.host}:{self.port}")
        
        # Start fault tolerance monitoring
        self.fault_manager.start()
        
        # Start Flask server
        self.app.run(host=self.host, port=self.port, threaded=True)
    
    def handle_transaction(self):
        """Handle transaction request"""
        try:
            data = request.json
            transaction_id = data.get('transaction_id', f"txn-{int(time.time() * 1000)}")
            operations = data.get('operations', [])
            
            logger.info(f"Received transaction {transaction_id} with {len(operations)} operations")
            
            # Coordinate transaction using 2PC
            result = self.transaction_manager.execute_transaction(transaction_id, operations)
            
            return jsonify({
                'transaction_id': transaction_id,
                'status': result['status'],
                'message': result.get('message', ''),
                'latency_ms': result.get('latency_ms', 0)
            }), 200
            
        except Exception as e:
            logger.error(f"Error handling transaction: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def handle_load_balance(self):
        """Handle load balancing request"""
        try:
            data = request.json
            request_type = data.get('type', 'edge')
            
            target_node = self.load_balancer.select_node(request_type)
            
            return jsonify({
                'node_id': target_node['node_id'],
                'host': target_node['host'],
                'port': target_node['port']
            }), 200
            
        except Exception as e:
            logger.error(f"Error in load balancing: {e}", exc_info=True)
            return jsonify({'error': str(e)}), 500
    
    def get_metrics(self):
        """Get node metrics"""
        system_metrics = get_system_metrics()
        request_metrics = self.metrics.get_metrics()
        
        return jsonify({
            'node_id': self.node_id,
            'node_type': 'core',
            'system': system_metrics,
            'requests': request_metrics,
            'transactions': self.transaction_manager.get_statistics(),
            'fault_tolerance': self.fault_manager.get_status()
        }), 200
    
    def health_check(self):
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'node_id': self.node_id,
            'timestamp': time.time()
        }), 200
    
    def stop(self):
        """Stop the core node"""
        self.running = False
        self.fault_manager.stop()
        logger.info(f"Stopping core node {self.node_id}")

if __name__ == '__main__':
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config/core_config.json'
    node = CoreNode(config_path)
    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()
