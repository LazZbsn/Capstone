#!/bin/bash

# Diagnostic script to check system status

echo "========================================="
echo "System Status Check"
echo "========================================="
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated"
    echo "   Run: source venv/bin/activate"
else
    echo "✅ Virtual environment: $VIRTUAL_ENV"
fi
echo ""

# Check if processes are running
echo "Checking running processes..."
ps aux | grep -E "(edge_node|core_node|cloud_node|gui_server)" | grep -v grep
echo ""

# Check if ports are listening
echo "Checking ports..."
for port in 5001 5002 5003 6001 6002 7001 7002 8080; do
    if netstat -tuln 2>/dev/null | grep -q ":$port " || ss -tuln 2>/dev/null | grep -q ":$port "; then
        echo "✅ Port $port is listening"
    else
        echo "❌ Port $port is NOT listening"
    fi
done
echo ""

# Check logs directory
echo "Checking logs directory..."
if [ -d "logs" ]; then
    echo "✅ Logs directory exists"
    echo "Recent log files:"
    ls -lth logs/*.log 2>/dev/null | head -10
    
    echo ""
    echo "--- Checking for errors in logs ---"
    for logfile in logs/*.log; do
        if [ -f "$logfile" ]; then
            errors=$(grep -i "error\|exception\|traceback\|failed" "$logfile" | tail -3)
            if [ ! -z "$errors" ]; then
                echo ""
                echo "❌ Errors in $(basename $logfile):"
                echo "$errors"
            fi
        fi
    done
else
    echo "❌ Logs directory not found"
fi
echo ""

# Check PID files
echo "Checking PID files..."
if [ -d "logs" ]; then
    for pidfile in logs/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            name=$(basename "$pidfile" .pid)
            if ps -p "$pid" > /dev/null 2>&1; then
                echo "✅ $name is running (PID: $pid)"
            else
                echo "❌ $name is NOT running (PID: $pid)"
            fi
        fi
    done
fi
echo ""

# Try to connect to nodes
echo "Testing node connectivity..."
for port in 5001 6001 7001 8080; do
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "http://localhost:$port/api/health" 2>/dev/null | grep -q "200\|404\|405"; then
        echo "✅ Port $port is responding"
    else
        echo "❌ Port $port is NOT responding"
    fi
done
echo ""

echo "========================================="
echo "To view specific log:"
echo "  tail -f logs/gui.log"
echo "  tail -f logs/edge-1.log"
echo ""
echo "To restart system:"
echo "  ./stop.sh"
echo "  ./deploy.sh"
echo "========================================="
