"""Metrics collection and monitoring"""
import time
import threading
from collections import deque
from typing import Dict, List
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Prometheus metrics
request_counter = Counter('requests_total', 'Total requests', ['node_type', 'operation', 'status'])
request_latency = Histogram('request_latency_seconds', 'Request latency', ['node_type', 'operation'])
active_connections = Gauge('active_connections', 'Active connections', ['node_type'])
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage', ['node_type'])
memory_usage = Gauge('memory_usage_percent', 'Memory usage percentage', ['node_type'])

class MetricsCollector:
    """Collect and aggregate system metrics"""
    
    def __init__(self, node_type: str, metrics_port: int = 9090):
        self.node_type = node_type
        self.metrics_port = metrics_port
        self.request_history = deque(maxlen=1000)
        self.latency_history = deque(maxlen=1000)
        self.start_time = time.time()
        self.lock = threading.Lock()
        
        # Start Prometheus metrics server
        try:
            start_http_server(self.metrics_port)
        except:
            pass  # Port might already be in use
    
    def record_request(self, operation: str, success: bool, latency_ms: float):
        """Record a request metric"""
        with self.lock:
            self.request_history.append({
                'operation': operation,
                'success': success,
                'latency_ms': latency_ms,
                'timestamp': time.time()
            })
            self.latency_history.append(latency_ms)
        
        request_counter.labels(
            node_type=self.node_type,
            operation=operation,
            status='success' if success else 'error'
        ).inc()
        
        request_latency.labels(
            node_type=self.node_type,
            operation=operation
        ).observe(latency_ms / 1000.0)
    
    def get_metrics(self) -> Dict:
        """Get aggregated metrics"""
        with self.lock:
            if not self.request_history:
                return {
                    'total_requests': 0,
                    'success_rate': 0.0,
                    'avg_latency_ms': 0.0,
                    'p95_latency_ms': 0.0,
                    'p99_latency_ms': 0.0,
                    'requests_per_second': 0.0,
                    'uptime_seconds': time.time() - self.start_time
                }
            
            total = len(self.request_history)
            successful = sum(1 for r in self.request_history if r['success'])
            latencies = sorted(self.latency_history)
            
            return {
                'total_requests': total,
                'success_rate': (successful / total) * 100.0,
                'avg_latency_ms': sum(self.latency_history) / len(self.latency_history),
                'p95_latency_ms': latencies[int(len(latencies) * 0.95)] if latencies else 0,
                'p99_latency_ms': latencies[int(len(latencies) * 0.99)] if latencies else 0,
                'requests_per_second': total / (time.time() - self.start_time),
                'uptime_seconds': time.time() - self.start_time
            }
