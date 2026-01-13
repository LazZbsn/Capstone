# PowerShell stop script for Windows

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Stopping Distributed Telecom System" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Stop all nodes by PID files
if (Test-Path "logs") {
    Get-ChildItem "logs\*.pid" | ForEach-Object {
        $pid = Get-Content $_.FullName
        $name = $_.BaseName
        
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped $name (PID: $pid)" -ForegroundColor Green
        } catch {
            Write-Host "Could not stop $name (PID: $pid may not exist)" -ForegroundColor Yellow
        }
        
        Remove-Item $_.FullName
    }
}

# Kill remaining Python processes for our nodes
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*edge_node.py*" -or
    $_.CommandLine -like "*core_node.py*" -or
    $_.CommandLine -like "*cloud_node.py*" -or
    $_.CommandLine -like "*gui_server.py*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "All nodes stopped." -ForegroundColor Green
Write-Host ""
