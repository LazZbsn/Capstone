"""Web GUI Dashboard for monitoring and control"""
import json
import time
import logging
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import requests
import threading
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML Template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Distributed Telecom System - Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .metric:last-child {
            border-bottom: none;
        }
        .metric-label {
            font-weight: 600;
            color: #555;
        }
        .metric-value {
            color: #667eea;
            font-weight: bold;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        .status.healthy {
            background: #4caf50;
            color: white;
        }
        .status.unhealthy {
            background: #f44336;
            color: white;
        }
        .control-panel {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
            font-size: 14px;
        }
        .btn:hover {
            background: #5568d3;
        }
        .transaction-form {
            margin-top: 20px;
        }
        .form-group {
            margin: 10px 0;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        .form-group input, .form-group textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
        .chart-container {
            height: 200px;
            margin-top: 10px;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        <h1>🚀 Distributed Telecom System Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h2>Edge Nodes</h2>
                <div id="edge-nodes">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>Core Nodes</h2>
                <div id="core-nodes">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>Cloud Nodes</h2>
                <div id="cloud-nodes">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>Transaction Statistics</h2>
                <div id="transactions">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>System Performance</h2>
                <div id="performance">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="card">
                <h2>Fault Tolerance</h2>
                <div id="fault-tolerance">
                    <div class="loading">Loading...</div>
                </div>
            </div>
        </div>
        
        <div class="control-panel">
            <h2>System Control</h2>
            <button class="btn" onclick="sendTestRequest()">Send Test Request</button>
            <button class="btn" onclick="startTransaction()">Start Transaction</button>
            <button class="btn" onclick="refreshAll()">Refresh All</button>
            
            <div class="transaction-form">
                <h3>Create Transaction</h3>
                <div class="form-group">
                    <label>Operation Type:</label>
                    <input type="text" id="op-type" placeholder="e.g., write, read">
                </div>
                <div class="form-group">
                    <label>Data (JSON):</label>
                    <textarea id="op-data" rows="3" placeholder='{"key": "value"}'></textarea>
                </div>
                <button class="btn" onclick="executeTransaction()">Execute Transaction</button>
            </div>
        </div>
    </div>
    
    <script>
        const EDGE_PORTS = [5001, 5002, 5003];
        const CORE_PORTS = [6001, 6002];
        const CLOUD_PORTS = [7001, 7002];
        
        async function fetchMetrics(port, nodeType) {
            try {
                const response = await fetch(`http://localhost:${port}/api/metrics`);
                return await response.json();
            } catch (e) {
                return { error: 'Node unavailable' };
            }
        }
        
        async function updateDashboard() {
            // Update Edge Nodes
            const edgeHtml = await Promise.all(EDGE_PORTS.map(async (port) => {
                const metrics = await fetchMetrics(port, 'edge');
                if (metrics.error) {
                    return `<div class="metric"><span class="metric-label">Edge Node (${port})</span><span class="status unhealthy">Offline</span></div>`;
                }
                const latency = metrics.requests?.avg_latency_ms?.toFixed(2) || '0';
                const rps = metrics.requests?.requests_per_second?.toFixed(2) || '0';
                return `
                    <div class="metric">
                        <span class="metric-label">Edge Node (${port})</span>
                        <span class="status healthy">Online</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Avg Latency</span>
                        <span class="metric-value">${latency} ms</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Requests/sec</span>
                        <span class="metric-value">${rps}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">CPU</span>
                        <span class="metric-value">${metrics.system?.cpu_percent?.toFixed(1) || '0'}%</span>
                    </div>
                `;
            }));
            document.getElementById('edge-nodes').innerHTML = edgeHtml.join('');
            
            // Update Core Nodes
            const coreHtml = await Promise.all(CORE_PORTS.map(async (port) => {
                const metrics = await fetchMetrics(port, 'core');
                if (metrics.error) {
                    return `<div class="metric"><span class="metric-label">Core Node (${port})</span><span class="status unhealthy">Offline</span></div>`;
                }
                const transactions = metrics.transactions || {};
                return `
                    <div class="metric">
                        <span class="metric-label">Core Node (${port})</span>
                        <span class="status healthy">Online</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Transactions</span>
                        <span class="metric-value">${transactions.total || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Commit Rate</span>
                        <span class="metric-value">${transactions.commit_rate?.toFixed(1) || '0'}%</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Active TXNs</span>
                        <span class="metric-value">${transactions.active_transactions || 0}</span>
                    </div>
                `;
            }));
            document.getElementById('core-nodes').innerHTML = coreHtml.join('');
            
            // Update Cloud Nodes
            const cloudHtml = await Promise.all(CLOUD_PORTS.map(async (port) => {
                const metrics = await fetchMetrics(port, 'cloud');
                if (metrics.error) {
                    return `<div class="metric"><span class="metric-label">Cloud Node (${port})</span><span class="status unhealthy">Offline</span></div>`;
                }
                return `
                    <div class="metric">
                        <span class="metric-label">Cloud Node (${port})</span>
                        <span class="status healthy">Online</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Role</span>
                        <span class="metric-value">${metrics.replication_role || 'unknown'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Data Items</span>
                        <span class="metric-value">${metrics.data_store_size || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Memory</span>
                        <span class="metric-value">${metrics.system?.memory_percent?.toFixed(1) || '0'}%</span>
                    </div>
                `;
            }));
            document.getElementById('cloud-nodes').innerHTML = cloudHtml.join('');
            
            // Get core node for transaction stats
            const coreMetrics = await fetchMetrics(CORE_PORTS[0], 'core');
            if (coreMetrics.transactions) {
                const txn = coreMetrics.transactions;
                document.getElementById('transactions').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Total</span>
                        <span class="metric-value">${txn.total || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Committed</span>
                        <span class="metric-value" style="color: #4caf50;">${txn.committed || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Aborted</span>
                        <span class="metric-value" style="color: #f44336;">${txn.aborted || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Success Rate</span>
                        <span class="metric-value">${txn.commit_rate?.toFixed(2) || '0'}%</span>
                    </div>
                `;
            }
            
            // Performance metrics
            const edgeMetrics = await fetchMetrics(EDGE_PORTS[0], 'edge');
            if (edgeMetrics.system) {
                document.getElementById('performance').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Avg Latency</span>
                        <span class="metric-value">${edgeMetrics.requests?.avg_latency_ms?.toFixed(2) || '0'} ms</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">P95 Latency</span>
                        <span class="metric-value">${edgeMetrics.requests?.p95_latency_ms?.toFixed(2) || '0'} ms</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Throughput</span>
                        <span class="metric-value">${edgeMetrics.requests?.requests_per_second?.toFixed(2) || '0'} req/s</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Uptime</span>
                        <span class="metric-value">${(edgeMetrics.requests?.uptime_seconds / 60).toFixed(1) || '0'} min</span>
                    </div>
                `;
            }
            
            // Fault tolerance
            if (coreMetrics.fault_tolerance) {
                const ft = coreMetrics.fault_tolerance;
                document.getElementById('fault-tolerance').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Total Nodes</span>
                        <span class="metric-value">${ft.total_nodes || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Healthy</span>
                        <span class="metric-value" style="color: #4caf50;">${ft.healthy_nodes || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Failed</span>
                        <span class="metric-value" style="color: #f44336;">${ft.failed_nodes || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Availability</span>
                        <span class="metric-value">${ft.availability?.toFixed(2) || '0'}%</span>
                    </div>
                `;
            }
        }
        
        async function sendTestRequest() {
            try {
                const response = await fetch('http://localhost:5001/api/request', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        request_id: 'test-' + Date.now(),
                        operation: 'test',
                        data: {'test': 'data'}
                    })
                });
                const result = await response.json();
                alert('Request sent! Response: ' + JSON.stringify(result));
            } catch (e) {
                alert('Error: ' + e.message);
            }
        }
        
        async function executeTransaction() {
            const opType = document.getElementById('op-type').value;
            const opData = document.getElementById('op-data').value;
            
            try {
                const data = JSON.parse(opData);
                const response = await fetch('http://localhost:6001/api/transaction', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        transaction_id: 'txn-' + Date.now(),
                        operations: [{
                            operation_id: 'op-1',
                            node_id: 'cloud-1',
                            operation_type: opType,
                            parameters: data
                        }]
                    })
                });
                const result = await response.json();
                alert('Transaction: ' + result.status);
            } catch (e) {
                alert('Error: ' + e.message);
            }
        }
        
        function refreshAll() {
            updateDashboard();
        }
        
        // Auto-refresh every 2 seconds
        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
"""

app = Flask(__name__)
CORS(app)

"""@app.route('/')
def dashboard():
    """Serve the dashboard HTML"""
    return render_template_string(DASHBOARD_HTML)
"""
"""@app.route('/api/aggregate-metrics')
def aggregate_metrics():
    """Aggregate metrics from all nodes"""
    edge_ports = [5001, 5002, 5003]
    core_ports = [6001, 6002]
    cloud_ports = [7001, 7002]
    
    all_metrics = {
        'edge_nodes': [],
        'core_nodes': [],
        'cloud_nodes': []
    }
    
    for port in edge_ports:
        try:
            resp = requests.get(f'http://localhost:{port}/api/metrics', timeout=1)
            all_metrics['edge_nodes'].append(resp.json())
        except:
            pass
    
    for port in core_ports:
        try:
            resp = requests.get(f'http://localhost:{port}/api/metrics', timeout=1)
            all_metrics['core_nodes'].append(resp.json())
        except:
            pass
    
    for port in cloud_ports:
        try:
            resp = requests.get(f'http://localhost:{port}/api/metrics', timeout=1)
            all_metrics['cloud_nodes'].append(resp.json())
        except:
            pass
    
    return jsonify(all_metrics)
"""
"""Web GUI Dashboard for monitoring and control"""
from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)
CORS(app) # Enable CORS to prevent browser blocks

@app.route('/api/aggregate-metrics')
def aggregate_metrics():
    """Proxy metrics to ensure the Dashboard sees all nodes"""
    node_map = {
        'edge_nodes': [5001, 5002, 5003],
        'core_nodes': [6001, 6002],
        'cloud_nodes': [7001, 7002]
    }
    
    all_metrics = {k: [] for k in node_map}
    for category, ports in node_map.items():
        for port in ports:
            try:
                # Use a very short timeout to keep the dashboard responsive
                resp = requests.get(f'http://127.0.0.1:{port}/api/metrics', timeout=0.8)
                if resp.status_code == 200:
                    all_metrics[category].append(resp.json())
                else:
                    all_metrics[category].append({"port": port, "status": "unhealthy"})
            except Exception:
                all_metrics[category].append({"port": port, "status": "offline"})
    
    return jsonify(all_metrics)

# Standard template logic continues below...
if __name__ == '__main__':
    print("Starting GUI Dashboard on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)
