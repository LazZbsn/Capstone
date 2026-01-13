"""Cloud Node - Persistent storage and analytics"""
import json
import time
import threading
import logging
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.common.utils import load_config, get_system_metrics, setup_logging
from src.common.metrics import MetricsCollector

setup_logging()
logger = logging.getLogger(__name__)

class CloudNode:
    """Cloud node implementation for persistent storage"""
    
    def __init__(self, config_path: str):
        self.config = load_config(config_path)
        self.node_id = self.config['node_id']
        self.host = self.config['host']
        self.port = self.config['port']
        
        # Database connection (simulated for now)
        self.db_config = self.config.get('database', {})
        self.replication_role = self.config.get('replication', {}).get('role', 'primary')
        
        # In-memory data store (replace with actual DB)
        self.data_store = {}
        self.replication_log = []
        
        # Metrics
        self.metrics = MetricsCollector('cloud', self.config['metrics']['port'])
        
        # Flask app
        self.app = Flask(__name__)
        self.app.route('/api/operation', methods=['POST'])(self.handle_operation)
        self.app.route('/api/prepare', methods=['POST'])(self.handle_prepare)
        self.app.route('/api/commit', methods=['POST'])(self.handle_commit)
        self.app.route('/api/metrics', methods=['GET'])(self.get_metrics)
        self.app.route('/api/health', methods=['GET'])(self.health_check)
        
        self.running = True
        logger.info(f"Cloud node {self.node_id} initialized as {self.replication_role}")
    
    def start(self):
        """Start the cloud node"""
        logger.info(f"Starting cloud node {self.node_id} on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, threaded=True)
    
    def handle_operation(self):
        """Handle data operation"""
        start_time = time.time()
        try:
            data = request.json
            operation = data.get('operation', 'read')
            key = data.get('key')
            value = data.get('value')
            
            if operation == 'read':
                result = self.data_store.get(key, None)
                success = result is not None
            elif operation == 'write':
                self.data_store[key] = {
                    'value': value,
                    'timestamp': time.time(),
                    'node_id': self.node_id
                }
                # Replicate to replicas if primary
                if self.replication_role == 'primary':
                    self._replicate_to_replicas('write', key, value)
                result = {'status': 'written'}
                success = True
            else:
                result = {'error': 'Unknown operation'}
                success = False
            
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_request(operation, success, latency_ms)
            
            return jsonify({
                'success': success,
                'result': result,
                'latency_ms': latency_ms
            }), 200
            
        except Exception as e:
            logger.error(f"Error handling operation: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def handle_prepare(self):
        """Handle transaction prepare phase"""
        try:
            data = request.json
            transaction_id = data.get('transaction_id')
            operations = data.get('operations', [])
            
            # Check if can commit
            can_commit = True
            for op in operations:
                # Validate operation
                if op.get('operation_type') == 'write':
                    # Check for conflicts, etc.
                    pass
            
            return jsonify({
                'transaction_id': transaction_id,
                'can_commit': can_commit,
                'node_id': self.node_id
            }), 200
            
        except Exception as e:
            logger.error(f"Error in prepare: {e}", exc_info=True)
            return jsonify({
                'can_commit': False,
                'error': str(e)
            }), 500
    
    def handle_commit(self):
        """Handle transaction commit"""
        try:
            data = request.json
            transaction_id = data.get('transaction_id')
            commit = data.get('commit', True)
            operations = data.get('operations', [])
            
            if commit:
                # Execute operations
                for op in operations:
                    if op.get('operation_type') == 'write':
                        key = op.get('parameters', {}).get('key')
                        value = op.get('parameters', {}).get('value')
                        self.data_store[key] = {
                            'value': value,
                            'timestamp': time.time(),
                            'node_id': self.node_id,
                            'transaction_id': transaction_id
                        }
            
            return jsonify({
                'transaction_id': transaction_id,
                'status': 'committed' if commit else 'aborted',
                'node_id': self.node_id
            }), 200
            
        except Exception as e:
            logger.error(f"Error in commit: {e}", exc_info=True)
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500
    
    def _replicate_to_replicas(self, operation: str, key: str, value: Any):
        """Replicate data to replica nodes"""
        replicas = self.config.get('replication', {}).get('replicas', [])
        for replica in replicas:
            try:
                # TODO: Send replication request to replica
                self.replication_log.append({
                    'operation': operation,
                    'key': key,
                    'value': value,
                    'timestamp': time.time(),
                    'replica': replica
                })
            except Exception as e:
                logger.error(f"Failed to replicate to {replica}: {e}")
    
    def get_metrics(self):
        """Get node metrics"""
        system_metrics = get_system_metrics()
        request_metrics = self.metrics.get_metrics()
        
        return jsonify({
            'node_id': self.node_id,
            'node_type': 'cloud',
            'replication_role': self.replication_role,
            'system': system_metrics,
            'requests': request_metrics,
            'data_store_size': len(self.data_store)
        }), 200
    
    def health_check(self):
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'node_id': self.node_id,
            'timestamp': time.time()
        }), 200
    
    def stop(self):
        """Stop the cloud node"""
        self.running = False
        logger.info(f"Stopping cloud node {self.node_id}")

if __name__ == '__main__':
    import sys
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config/cloud_config.json'
    node = CloudNode(config_path)
    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()
