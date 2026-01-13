#!/usr/bin/env python3
"""Test script for the distributed telecom system"""
import requests
import time
import json
from typing import Dict

BASE_URLS = {
    'edge': ['http://localhost:5001', 'http://localhost:5002', 'http://localhost:5003'],
    'core': ['http://localhost:6001', 'http://localhost:6002'],
    'cloud': ['http://localhost:7001', 'http://localhost:7002'],
    'gui': 'http://localhost:8080'
}

def test_edge_node(url: str) -> bool:
    """Test edge node health"""
    try:
        response = requests.get(f"{url}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_core_node(url: str) -> bool:
    """Test core node health"""
    try:
        response = requests.get(f"{url}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def test_cloud_node(url: str) -> bool:
    """Test cloud node health"""
    try:
        response = requests.get(f"{url}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def send_test_request(edge_url: str) -> Dict:
    """Send a test request to edge node"""
    try:
        response = requests.post(
            f"{edge_url}/api/request",
            json={
                'request_id': f'test-{int(time.time() * 1000)}',
                'operation': 'test_operation',
                'data': {'key': 'test_value', 'timestamp': time.time()}
            },
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {'error': str(e)}

def create_test_transaction(core_url: str) -> Dict:
    """Create a test transaction"""
    try:
        response = requests.post(
            f"{core_url}/api/transaction",
            json={
                'transaction_id': f'txn-{int(time.time() * 1000)}',
                'operations': [
                    {
                        'operation_id': 'op-1',
                        'node_id': 'cloud-1',
                        'operation_type': 'write',
                        'parameters': {
                            'key': 'test_key',
                            'value': 'test_value'
                        }
                    }
                ]
            },
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {'error': str(e)}

def get_metrics(url: str, node_type: str) -> Dict:
    """Get node metrics"""
    try:
        response = requests.get(f"{url}/api/metrics", timeout=2)
        return response.json()
    except:
        return {'error': 'Unable to fetch metrics'}

def main():
    print("=" * 60)
    print("Distributed Telecom System - Test Suite")
    print("=" * 60)
    print()
    
    # Test Edge Nodes
    print("Testing Edge Nodes...")
    edge_results = []
    for i, url in enumerate(BASE_URLS['edge'], 1):
        status = test_edge_node(url)
        edge_results.append((f"Edge-{i}", url, status))
        print(f"  Edge-{i} ({url}): {'✓ Online' if status else '✗ Offline'}")
    print()
    
    # Test Core Nodes
    print("Testing Core Nodes...")
    core_results = []
    for i, url in enumerate(BASE_URLS['core'], 1):
        status = test_core_node(url)
        core_results.append((f"Core-{i}", url, status))
        print(f"  Core-{i} ({url}): {'✓ Online' if status else '✗ Offline'}")
    print()
    
    # Test Cloud Nodes
    print("Testing Cloud Nodes...")
    cloud_results = []
    for i, url in enumerate(BASE_URLS['cloud'], 1):
        status = test_cloud_node(url)
        cloud_results.append((f"Cloud-{i}", url, status))
        print(f"  Cloud-{i} ({url}): {'✓ Online' if status else '✗ Offline'}")
    print()
    
    # Test Request Flow
    print("Testing Request Flow...")
    online_edges = [url for _, url, status in edge_results if status]
    if online_edges:
        result = send_test_request(online_edges[0])
        if 'error' not in result:
            print(f"  ✓ Request successful: {result.get('success', False)}")
            print(f"    Latency: {result.get('latency_ms', 0):.2f} ms")
            print(f"    From Cache: {result.get('from_cache', False)}")
        else:
            print(f"  ✗ Request failed: {result['error']}")
    else:
        print("  ✗ No edge nodes available for testing")
    print()
    
    # Test Transaction
    print("Testing Distributed Transaction...")
    online_cores = [url for _, url, status in core_results if status]
    if online_cores:
        result = create_test_transaction(online_cores[0])
        if 'error' not in result:
            print(f"  ✓ Transaction Status: {result.get('status', 'unknown')}")
            print(f"    Latency: {result.get('latency_ms', 0):.2f} ms")
        else:
            print(f"  ✗ Transaction failed: {result['error']}")
    else:
        print("  ✗ No core nodes available for testing")
    print()
    
    # Display Metrics
    print("System Metrics Summary:")
    print("-" * 60)
    
    if online_edges:
        metrics = get_metrics(online_edges[0], 'edge')
        if 'error' not in metrics:
            print(f"Edge Node ({online_edges[0]}):")
            print(f"  CPU: {metrics.get('system', {}).get('cpu_percent', 0):.1f}%")
            print(f"  Memory: {metrics.get('system', {}).get('memory_percent', 0):.1f}%")
            req_metrics = metrics.get('requests', {})
            print(f"  Requests: {req_metrics.get('total_requests', 0)}")
            print(f"  Avg Latency: {req_metrics.get('avg_latency_ms', 0):.2f} ms")
    
    if online_cores:
        metrics = get_metrics(online_cores[0], 'core')
        if 'error' not in metrics:
            print(f"\nCore Node ({online_cores[0]}):")
            print(f"  CPU: {metrics.get('system', {}).get('cpu_percent', 0):.1f}%")
            txn = metrics.get('transactions', {})
            print(f"  Transactions: {txn.get('total', 0)}")
            print(f"  Commit Rate: {txn.get('commit_rate', 0):.2f}%")
    
    if online_cores:
        ft = metrics.get('fault_tolerance', {})
        if ft:
            print(f"\nFault Tolerance:")
            print(f"  Healthy Nodes: {ft.get('healthy_nodes', 0)}/{ft.get('total_nodes', 0)}")
            print(f"  Availability: {ft.get('availability', 0):.2f}%")
    
    print()
    print("=" * 60)
    print("Test Summary:")
    print(f"  Edge Nodes: {sum(1 for _, _, s in edge_results if s)}/{len(edge_results)} online")
    print(f"  Core Nodes: {sum(1 for _, _, s in core_results if s)}/{len(core_results)} online")
    print(f"  Cloud Nodes: {sum(1 for _, _, s in cloud_results if s)}/{len(cloud_results)} online")
    print()
    print(f"GUI Dashboard: {BASE_URLS['gui']}")
    print("=" * 60)

if __name__ == '__main__':
    main()
