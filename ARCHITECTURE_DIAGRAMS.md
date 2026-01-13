# Architecture Diagrams

This document contains visual representations of the system architecture.

## 1. System Overview Diagram

```
                    ┌──────────────────────────────────────────┐
                    │   Distributed Telecom System             │
                    │   Edge-Core-Cloud Architecture           │
                    └──────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              Client Layer                                    │
│                         (Web Browser, Mobile App)                           │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Load Balancer (Nginx)                              │
│                      Routes requests to Edge Nodes                           │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
        ┌──────────┐     ┌──────────┐     ┌──────────┐
        │ Edge-1   │     │ Edge-2   │     │ Edge-3   │
        │ :5001    │     │ :5002    │     │ :5003    │
        │ Cache    │     │ Cache    │     │ Cache    │
        └────┬─────┘     └────┬─────┘     └────┬─────┘
             │                │                │
             └────────┬───────┴────────────────┘
                      │ RPC Calls
                      ▼
        ┌─────────────────────────────┐
        │      Core Nodes Layer        │
        ├─────────────────────────────┤
        │  Core-1 (:6001) Primary     │
        │  Core-2 (:6002) Secondary   │
        │  - Transaction Coordinator  │
        │  - Load Balancer            │
        │  - Fault Manager            │
        └─────────────┬───────────────┘
                      │ Distributed Transactions (2PC)
                      ▼
        ┌─────────────────────────────┐
        │      Cloud Nodes Layer       │
        ├─────────────────────────────┤
        │  Cloud-1 (:7001) Primary    │
        │  Cloud-2 (:7002) Replica    │
        │  - Persistent Storage       │
        │  - Data Replication         │
        │  - Analytics                │
        └─────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │      Data Layer              │
        │  PostgreSQL / MongoDB        │
        │  Redis Cache                 │
        └─────────────────────────────┘
```

## 2. Transaction Flow Diagram (2PC)

```
Client Request
    │
    ▼
Edge Node
    │
    │ HTTP POST /api/request
    ▼
Core Node (Coordinator)
    │
    ├─── Phase 1: PREPARE ─────────────────────┐
    │                                           │
    │  ┌──────────┐    ┌──────────┐           │
    │  │ Cloud-1  │    │ Cloud-2  │           │
    │  │ (Participant) │ (Participant)        │
    │  └────┬─────┘    └────┬─────┘           │
    │       │               │                  │
    │       ▼ YES           ▼ YES              │
    │  ┌──────────────────────────┐            │
    │  │ All Prepared?            │            │
    │  └─────┬────────────────────┘            │
    │        │                                  │
    │        ├─── Phase 2: COMMIT ─────────────┤
    │        │                                  │
    │        ▼                                  │
    │  ┌──────────┐    ┌──────────┐           │
    │  │ Cloud-1  │    │ Cloud-2  │           │
    │  │ COMMIT   │    │ COMMIT   │           │
    │  └────┬─────┘    └────┬─────┘           │
    │       │               │                  │
    │       ▼ ACK           ▼ ACK              │
    │  ┌──────────────────────────┐            │
    │  │ Transaction Committed    │            │
    │  └──────────────────────────┘            │
    │                                           │
    └───────────────────────────────────────────┘
    │
    ▼
Response to Client
```

## 3. Fault Tolerance Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Primary Node (Active)                     │
│                    Processing Requests                       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Heartbeat & State Replication
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Replica 1│     │ Replica 2│     │ Replica 3│
│ (Standby)│     │ (Standby)│     │ (Standby)│
└──────────┘     └──────────┘     └──────────┘

Failure Detection:
    ├── Heartbeat Timeout (> 10s)
    ├── No Response to Requests
    └── Inconsistent Behavior (Byzantine)

Recovery Process:
    1. Detect Failure
    2. Elect New Primary (Consensus)
    3. Promote Replica to Primary
    4. Synchronize State
    5. Resume Service
```

## 4. Load Balancing Strategy

```
Request Arrives
    │
    ▼
┌─────────────────┐
│ Load Balancer   │
│ (Core Node)     │
└────────┬────────┘
         │
         ├── Check Node Health
         │   ├── Heartbeat Status
         │   ├── CPU Usage
         │   ├── Memory Usage
         │   └── Active Connections
         │
         ├── Apply Selection Algorithm
         │   ├── Round-Robin (default)
         │   ├── Least Connections
         │   ├── Weighted Round-Robin
         │   └── Least CPU/Memory
         │
         ▼
┌─────────────────┐
│ Selected Node   │
└─────────────────┘
```

## 5. Data Replication Flow

```
Write Request
    │
    ▼
┌──────────┐
│ Primary  │
│ (Cloud-1)│
└────┬─────┘
     │
     ├── Write to Local DB
     │
     ├── Replicate to Replicas ────┐
     │                              │
     │                              ▼
     │                    ┌─────────────┐
     │                    │   Replica 1  │
     │                    │   (Cloud-2)  │
     │                    └─────────────┘
     │
     └── Send ACK to Client

Read Request
    │
    ├── Primary Read (Strong Consistency)
    │
    └── Replica Read (Eventual Consistency)
        └── Used for read scaling
```

## 6. Communication Protocol Stack

```
┌─────────────────────────────────────┐
│     Application Layer (HTTP/REST)   │
├─────────────────────────────────────┤
│     RPC Layer (gRPC)                │
├─────────────────────────────────────┤
│     Message Queue (RabbitMQ)        │
├─────────────────────────────────────┤
│     Transport Layer (TCP/IP)        │
└─────────────────────────────────────┘

Communication Patterns:
    - Edge ↔ Core: HTTP/REST + gRPC
    - Core ↔ Cloud: gRPC (Transactions)
    - Node ↔ Node: Heartbeat (gRPC)
    - Async Events: RabbitMQ
```

## 7. Performance Metrics Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Edge    │     │  Core    │     │  Cloud   │
│  Nodes   │     │  Nodes   │     │  Nodes   │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     │ Metrics        │ Metrics        │ Metrics
     │ (Prometheus)   │ (Prometheus)   │ (Prometheus)
     └────┬───────────┼────────────────┘
          │           │
          ▼           ▼
    ┌──────────────────────┐
    │  Metrics Aggregator  │
    │  (Prometheus Server) │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │   GUI Dashboard      │
    │   (:8080)            │
    │   - Visualizations   │
    │   - Real-time Updates│
    └──────────────────────┘
```

## 8. Deployment Topology

```
┌─────────────────────────────────────────────────────────┐
│              Physical/VM Deployment                      │
└─────────────────────────────────────────────────────────┘

Server 1 (Edge Zone)          Server 2 (Core Zone)
┌─────────────┐              ┌─────────────┐
│ Edge-1      │              │ Core-1      │
│ Edge-2      │◄─────────────┤ Core-2      │
└─────────────┘  Network     └──────┬──────┘
                                     │
Server 3 (Edge Zone)                │
┌─────────────┐                     │
│ Edge-3      │                     │
└─────────────┘                     │
                                     ▼
                            Server 4 (Cloud Zone)
                            ┌─────────────┐
                            │ Cloud-1     │
                            │ Cloud-2     │
                            │ Database    │
                            └─────────────┘

Load Distribution:
    - Edge: High throughput, low latency
    - Core: Medium load, coordination
    - Cloud: High capacity, persistence
```

## 9. Security Architecture

```
┌─────────────────────────────────────────┐
│          External Clients               │
└──────────────┬──────────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────────┐
│          API Gateway / WAF              │
│          - Authentication               │
│          - Rate Limiting                │
│          - SSL/TLS Termination          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│          Internal Network               │
│          (Private Network)              │
│                                         │
│  ┌────────┐  ┌────────┐  ┌────────┐   │
│  │ Edge   │  │ Core   │  │ Cloud  │   │
│  │ Nodes  │  │ Nodes  │  │ Nodes  │   │
│  └────────┘  └────────┘  └────────┘   │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│          Database Layer                 │
│          - Encrypted at Rest            │
│          - Access Control               │
└─────────────────────────────────────────┘
```

These diagrams provide a comprehensive view of how all components interact and communicate in the distributed system.
