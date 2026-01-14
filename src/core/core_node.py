"""Core Node - Coordinates transactions and load balancing"""
import time
import logging
from flask import Flask, request, jsonify
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.common.utils import load_config, get_system_metrics, setup_logging
from src.common.metrics import MetricsCollector
from src.transactions.transaction_manager import TransactionManager
from src.fault_tolerance.fault_manager import FaultManager
from src.core.load_balancer import LoadBalancer

setup_logging()
logger = logging.getLogger(__name__)

class CoreNode:
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.node_id = self.config['node_id']
        self.host = self.config['host']
        self.port = self.config['port']
        
        # Core components for Transactions and Fault Tolerance (Task 3 & 4)
        self.transaction_manager = TransactionManager(self.config.get('transaction', {}))
        self.fault_manager = FaultManager(self.config.get('fault_tolerance', {}), self.node_id)
        self.load_balancer = LoadBalancer(self.config.get('edge_nodes', []), self.config.get('cloud_nodes', []))
        
        self.metrics = MetricsCollector('core', self.config['metrics']['port'])
        self.app = Flask(__name__)
        
        # Standardized API Endpoints
        self.app.route('/api/transaction', methods=['POST'])(self.handle_transaction)
        self.app.route('/api/balance', methods=['POST'])(self.handle_load_balance)
        self.app.route('/api/metrics', methods=['GET'])(self.get_metrics)
        self.app.route('/api/health', methods=['GET'])(self.health_check)
        
        logger.info(f"Core node {self.node_id} initialized")

    def start(self):
        """Starts the coordination and fault monitoring services"""
        self.fault_manager.start()
        self.app.run(host=self.host, port=self.port, threaded=True)

    def handle_transaction(self):
        """Coordinates Distributed Transactions using 2PC logic"""
        try:
            data = request.json
            txn_id = data.get('transaction_id', f"txn-{int(time.time()*1000)}")
            ops = data.get('operations', [])
            
            # Coordination logic for Task 3
            result = self.transaction_manager.execute_transaction(txn_id, ops)
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Coordination failure: {e}")
            return jsonify({'status': 'ABORTED', 'error': str(e)}), 500

    def handle_load_balance(self):
        """Dynamic node selection based on real-time metrics (Task 5)"""
        try:
            request_type = request.json.get('type', 'edge')
            target = self.load_balancer.select_node(request_type, strategy='least_cpu')
            return jsonify(target), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def get_metrics(self):
        """Aggregates metrics for the GUI Dashboard"""
        return jsonify({
            'node_id': self.node_id, 
            'system': get_system_metrics(),
            'transactions': self.transaction_manager.get_statistics(),
            'fault_tolerance': self.fault_manager.get_status()
        }), 200

    def health_check(self):
        return jsonify({'status': 'healthy', 'node_id': self.node_id}), 200

if __name__ == '__main__':
    node = CoreNode(sys.argv[1] if len(sys.argv) > 1 else 'config/core_config.json')
    node.start()
