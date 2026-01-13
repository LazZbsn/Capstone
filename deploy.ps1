# PowerShell deployment script for Windows

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deploying Distributed Telecom System" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Activate virtual environment if exists
if (Test-Path "venv") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Function to start a process
function Start-Node {
    param(
        [string]$Name,
        [string]$Script,
        [string]$Config,
        [string]$Port
    )
    
    Write-Host "Starting $Name..." -ForegroundColor Green
    
    if ($Config) {
        $process = Start-Process python -ArgumentList $Script, $Config -PassThru -WindowStyle Hidden
    } else {
        $process = Start-Process python -ArgumentList $Script -PassThru -WindowStyle Hidden
    }
    
    $process.Id | Out-File "logs\$Name.pid"
    Start-Sleep -Seconds 1
    Write-Host "$Name started (PID: $($process.Id))" -ForegroundColor Green
}

# Start Edge Nodes
Write-Host "Starting Edge Nodes..." -ForegroundColor Yellow
Start-Node "edge-1" "src/edge/edge_node.py" "config/edge_config.json" "5001"

# Create configs for edge-2 and edge-3
$edge2Config = Get-Content "config/edge_config.json" -Raw | 
    ForEach-Object { $_ -replace '"node_id": "edge-1"', '"node_id": "edge-2"' } |
    ForEach-Object { $_ -replace '"port": 5001', '"port": 5002' }
$edge2Config | Out-File "config/edge_config_2.json" -Encoding UTF8

$edge3Config = Get-Content "config/edge_config.json" -Raw | 
    ForEach-Object { $_ -replace '"node_id": "edge-1"', '"node_id": "edge-3"' } |
    ForEach-Object { $_ -replace '"port": 5001', '"port": 5003' }
$edge3Config | Out-File "config/edge_config_3.json" -Encoding UTF8

Start-Node "edge-2" "src/edge/edge_node.py" "config/edge_config_2.json" "5002"
Start-Node "edge-3" "src/edge/edge_node.py" "config/edge_config_3.json" "5003"

# Start Core Nodes
Write-Host "Starting Core Nodes..." -ForegroundColor Yellow
Start-Node "core-1" "src/core/core_node.py" "config/core_config.json" "6001"

$core2Config = Get-Content "config/core_config.json" -Raw | 
    ForEach-Object { $_ -replace '"node_id": "core-1"', '"node_id": "core-2"' } |
    ForEach-Object { $_ -replace '"port": 6001', '"port": 6002"' } |
    ForEach-Object { $_ -replace '"coordinator_role": "primary"', '"coordinator_role": "secondary"' }
$core2Config | Out-File "config/core_config_2.json" -Encoding UTF8

Start-Node "core-2" "src/core/core_node.py" "config/core_config_2.json" "6002"

# Start Cloud Nodes
Write-Host "Starting Cloud Nodes..." -ForegroundColor Yellow
Start-Node "cloud-1" "src/cloud/cloud_node.py" "config/cloud_config.json" "7001"

$cloud2Config = Get-Content "config/cloud_config.json" -Raw | 
    ForEach-Object { $_ -replace '"node_id": "cloud-1"', '"node_id": "cloud-2"' } |
    ForEach-Object { $_ -replace '"port": 7001', '"port": 7002"' } |
    ForEach-Object { $_ -replace '"role": "primary"', '"role": "replica"' }
$cloud2Config | Out-File "config/cloud_config_2.json" -Encoding UTF8

Start-Node "cloud-2" "src/cloud/cloud_node.py" "config/cloud_config_2.json" "7002"

# Start GUI
Write-Host "Starting GUI Dashboard..." -ForegroundColor Yellow
Start-Node "gui" "src/gui/gui_server.py" "" "8080"

# Wait for services to start
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "All nodes started. Access the GUI at:" -ForegroundColor Green
Write-Host "  http://localhost:8080" -ForegroundColor Yellow
Write-Host ""
Write-Host "To stop all nodes, run: .\stop.ps1" -ForegroundColor Yellow
Write-Host ""
