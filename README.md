# Carrier-Grade Edge–Core–Cloud Distributed Telecommunication System

## Project Overview

This project implements a carrier-grade distributed telecommunication system spanning edge, core, and cloud nodes. The system supports high-throughput telecom services, distributed transactions, fault-tolerant operations, and optimizes latency, CPU/memory utilization, and network resources.

## Architecture

### System Components

1. **Edge Nodes**: Low-latency local processing, handle user requests directly
2. **Core Nodes**: Coordination, aggregation, load balancing, transaction coordination
3. **Cloud Nodes**: Centralized services, data persistence, analytics, long-term storage

### Communication Flow

```
User Request → Edge Node → Core Node → Cloud Node
              ↓ (cache)    ↓ (coord)   ↓ (persist)
              Response ← ← ← ← ← ← ← ← ←
```

## Features

- ✅ Distributed System Architecture & Resource Allocation
- ✅ RPC, Client-Server Messaging, Distributed Shared Memory
- ✅ Distributed Transactions (ACID, 2PC/3PC)
- ✅ Fault Tolerance (Crash, Omission, Byzantine failures)
- ✅ Dynamic Load Balancing & Process Management
- ✅ Performance Monitoring & Metrics
- ✅ Web-based GUI Dashboard

## Quick Start

1. **Install Dependencies**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Start the System**:
   ```bash
   ./deploy.sh
   ```

3. **Access GUI**:
   Open browser to `http://localhost:8080`

## Project Structure

```
.
├── README.md
├── ARCHITECTURE.md
├── setup.sh
├── deploy.sh
├── requirements.txt
├── config/
│   ├── edge_config.json
│   ├── core_config.json
│   └── cloud_config.json
├── src/
│   ├── edge/
│   ├── core/
│   ├── cloud/
│   ├── common/
│   ├── transactions/
│   ├── fault_tolerance/
│   └── gui/
└── tests/
```

## Performance Metrics

The system tracks:
- Latency (edge, core, cloud)
- Throughput (requests/sec)
- CPU/Memory utilization
- Transaction success rate
- Fault recovery time
- Network packet loss
