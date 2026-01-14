#!/bin/bash

# Stop script for Distributed Telecom System

echo "========================================="
echo "Stopping Distributed Telecom System"
echo "========================================="

# Stop all nodes by PID files
if [ -d "logs" ]; then
    for pidfile in logs/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            name=$(basename "$pidfile" .pid)
            if kill "$pid" 2>/dev/null; then
                echo "Stopped $name (PID: $pid)"
            else
                echo "Could not stop $name (PID: $pid may not exist)"
            fi
            rm "$pidfile"
        fi
    done
fi

# Also kill any remaining Python processes for our nodes
pkill -f "edge_node.py" 2>/dev/null
pkill -f "core_node.py" 2>/dev/null
pkill -f "cloud_node.py" 2>/dev/null
pkill -f "gui_server.py" 2>/dev/null

echo ""
echo "All nodes stopped."
echo ""
