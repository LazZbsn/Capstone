# System Architecture Documentation

## 1. Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Carrier-Grade Distributed System              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Edge Nodes  │────────▶│  Core Nodes  │────────▶│ Cloud Nodes  │
│  (3 nodes)   │◀────────│  (2 nodes)   │◀────────│  (2 nodes)   │
└──────────────┘         └──────────────┘         └──────────────┘
      │                         │                         │
      │                         │                         │
      ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Distributed Transaction Coordinator              │
│                    (2-Phase/3-Phase Commit)                      │
└─────────────────────────────────────────────────────────────────┘
      │                         │                         │
      ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              Fault Tolerance & Replication Manager                │
│         (Crash, Omission, Byzantine Failure Handling)            │
└─────────────────────────────────────────────────────────────────┘
      │                         │                         │
      ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Load Balancer & Scheduler                      │
│              (Dynamic Resource Allocation)                       │
└─────────────────────────────────────────────────────────────────┘
      │                         │                         │
      ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Monitoring GUI Dashboard                     │
│              (Real-time Metrics & Control)                       │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Node Communication Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Request Flow                    │
└─────────────────────────────────────────────────────────────┘

Client
  │
  │ HTTP/gRPC Request
  ▼
┌─────────────┐
│ Edge Node 1 │  ←─── Load Balancer (Round-robin/Least-loaded)
└─────────────┘
  │
  │ RPC Call
  ▼
┌─────────────┐
│ Core Node 1 │  ←─── Transaction Coordinator (Primary)
└─────────────┘
  │
  │ Distributed Transaction (2PC)
  ├─────────────┐
  │             │
  ▼             ▼
┌──────────┐  ┌──────────┐
│Cloud N1  │  │Cloud N2  │  ←─── Replication (Primary-Replica)
└──────────┘  └──────────┘
  │             │
  └─────┬───────┘
        │
        ▼
   Persistence Layer
```

## 3. Distributed Transaction Flow (2PC)

```
┌──────────────────────────────────────────────────────────────┐
│                   Two-Phase Commit Protocol                    │
└──────────────────────────────────────────────────────────────┘

Phase 1: Prepare
┌─────────────┐
│ Coordinator │
│  (Core N1)  │
└─────────────┘
      │
      │ PREPARE request
      ├─────────────────┐
      │                 │
      ▼                 ▼
┌─────────┐         ┌─────────┐
│Participant 1      │Participant 2
│(Cloud N1)         │(Cloud N2)
└─────────┘         └─────────┘
      │                 │
      │ YES/NO          │ YES/NO
      ▼                 ▼
┌─────────────┐
│ Coordinator │  ←─── Wait for all responses
│  (Core N1)  │
└─────────────┘

Phase 2: Commit/Abort
      │
      │ COMMIT/ABORT
      ├─────────────────┐
      │                 │
      ▼                 ▼
┌─────────┐         ┌─────────┐
│Participant 1      │Participant 2
│(Cloud N1)         │(Cloud N2)
└─────────┘         └─────────┘
      │                 │
      │ ACK             │ ACK
      ▼                 ▼
┌─────────────┐
│ Coordinator │  ←─── Transaction Complete
│  (Core N1)  │
└─────────────┘
```

## 4. Fault Tolerance Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Replication Strategy                         │
└──────────────────────────────────────────────────────────────┘

Primary Node (Active)
  │
  │ Replicate state/logs
  ├─────────────┐
  │             │
  ▼             ▼
Replica 1    Replica 2
(Standby)    (Standby)

On Primary Failure:
  1. Heartbeat timeout detected
  2. Replica promotion (election)
  3. State synchronization
  4. Service continuation

┌──────────────────────────────────────────────────────────────┐
│                  Failure Detection Mechanisms                   │
└──────────────────────────────────────────────────────────────┘

Edge Node Failure:
  ├── Load balancer routes to healthy edge nodes
  ├── Session state migrated
  └── Client reconnects transparently

Core Node Failure:
  ├── Secondary coordinator takes over
  ├── Transaction state recovered from logs
  └── Ongoing transactions aborted and retried

Cloud Node Failure:
  ├── Read requests routed to replicas
  ├── Write requests queued
  └── Replica promoted to primary
```

## 5. Load Balancing Strategy

```
┌──────────────────────────────────────────────────────────────┐
│              Dynamic Load Balancing Algorithm                   │
└──────────────────────────────────────────────────────────────┘

Request arrives
      │
      ▼
┌──────────────┐
│ Load Balancer│
└──────────────┘
      │
      ├── Check node health (heartbeat)
      ├── Get current load (CPU, memory, active connections)
      ├── Calculate weighted score
      │
      ▼
┌─────────────────────────────────┐
│ Selection Algorithm:             │
│  - Round-robin (baseline)        │
│  - Least connections             │
│  - Weighted round-robin          │
│  - Least CPU/memory usage        │
│  - Geographic proximity (edge)   │
└─────────────────────────────────┘
      │
      ▼
Route to selected node
```

## 6. Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Data Flow Diagram                          │
└──────────────────────────────────────────────────────────────┘

User Request
    │
    ▼
┌──────────────┐
│ Edge Cache   │  ←─── Fast local cache (Redis-like)
│ (Edge Node)  │
└──────────────┘
    │ Cache miss
    ▼
┌──────────────┐
│ Core Router  │  ←─── Request routing, aggregation
│ (Core Node)  │
└──────────────┘
    │
    ├── Simple read → Direct to cloud
    │
    └── Write/Complex → Transaction coordinator
                         │
                         ▼
                    ┌──────────────┐
                    │ Transaction  │
                    │  Manager     │
                    └──────────────┘
                         │
                         ▼
                    ┌──────────────┐
                    │ Cloud Store  │
                    │ (PostgreSQL/ │
                    │   MongoDB)   │
                    └──────────────┘
```

## 7. Component Responsibilities

### Edge Nodes
- Handle user requests (low latency < 10ms target)
- Local caching of frequently accessed data
- Request preprocessing and filtering
- Session management
- Load reporting to core

### Core Nodes
- Transaction coordination (2PC/3PC)
- Load balancing and routing
- Distributed consensus (Raft/Paxos-like)
- Event ordering and synchronization
- Inter-node communication coordination

### Cloud Nodes
- Persistent data storage
- Complex analytics and processing
- Long-term data retention
- Backup and replication
- Global data consistency

### Common Services
- **RPC Framework**: gRPC for inter-node communication
- **Distributed Shared Memory**: Redis Cluster for shared state
- **Message Queue**: RabbitMQ for async communication
- **Monitoring**: Prometheus metrics + Custom dashboard

## 8. Performance Targets

| Metric | Edge | Core | Cloud |
|--------|------|------|-------|
| Latency | < 10ms | < 50ms | < 200ms |
| Throughput | 10K req/s | 5K req/s | 2K req/s |
| CPU Usage | < 70% | < 80% | < 85% |
| Memory | < 2GB | < 4GB | < 8GB |
| Availability | 99.9% | 99.95% | 99.99% |

## 9. Technology Stack

- **Language**: Python 3.9+
- **RPC**: gRPC
- **Web Framework**: Flask (API) + React (GUI)
- **Database**: PostgreSQL (primary), MongoDB (analytics)
- **Cache**: Redis
- **Message Queue**: RabbitMQ
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Monitoring**: Prometheus + Grafana-like dashboard
