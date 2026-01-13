"""Common utility functions for the distributed system"""
import json
import time
import psutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)

def get_system_metrics() -> Dict[str, float]:
    """Get current system metrics (CPU, memory, etc.)"""
    return {
        'cpu_percent': psutil.cpu_percent(interval=0.1),
        'memory_percent': psutil.virtual_memory().percent,
        'memory_used_mb': psutil.virtual_memory().used / (1024 * 1024),
        'memory_total_mb': psutil.virtual_memory().total / (1024 * 1024),
        'timestamp': time.time()
    }

def setup_logging(level=logging.INFO, log_file: Optional[str] = None):
    """Setup logging configuration"""
    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def generate_node_id(prefix: str, index: int) -> str:
    """Generate a unique node ID"""
    return f"{prefix}-{index}"

def calculate_latency(start_time: float) -> float:
    """Calculate latency in milliseconds"""
    return (time.time() - start_time) * 1000
