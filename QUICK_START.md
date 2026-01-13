# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Setup Environment

**Linux/macOS:**
```bash
cd distributed-telecom-system
chmod +x setup.sh deploy.sh stop.sh
./setup.sh
```

**Windows:**
```powershell
cd distributed-telecom-system
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Deploy System

**Linux/macOS:**
```bash
./deploy.sh
```

**Windows:**
```powershell
.\deploy.ps1
```

**Docker:**
```bash
docker-compose up -d
```

### Step 3: Access Dashboard

Open your browser and go to: **http://localhost:8080**

## 📊 System Status

After deployment, you should have:

- ✅ 3 Edge Nodes running on ports 5001-5003
- ✅ 2 Core Nodes running on ports 6001-6002
- ✅ 2 Cloud Nodes running on ports 7001-7002
- ✅ 1 GUI Dashboard on port 8080

## 🧪 Test the System

Run the test script:
```bash
python test_system.py
```

Or manually test:
```bash
# Test Edge Node
curl http://localhost:5001/api/health

# Send a request
curl -X POST http://localhost:5001/api/request \
  -H "Content-Type: application/json" \
  -d '{"request_id": "test-1", "operation": "test", "data": {"key": "value"}}'
```

## 📖 Documentation

- **README.md** - Overview and features
- **ARCHITECTURE.md** - Detailed architecture
- **ARCHITECTURE_DIAGRAMS.md** - Visual diagrams
- **SETUP_GUIDE.md** - Complete setup instructions
- **PROJECT_SUMMARY.md** - Project summary

## 🛑 Stop the System

**Linux/macOS:**
```bash
./stop.sh
```

**Windows:**
```powershell
.\stop.ps1
```

**Docker:**
```bash
docker-compose down
```

## 🔧 Troubleshooting

1. **Port already in use?**
   - Check what's using the port: `netstat -an | grep <port>`
   - Kill the process or change port in config files

2. **Nodes not starting?**
   - Check logs in `logs/` directory
   - Ensure virtual environment is activated
   - Verify dependencies: `pip install -r requirements.txt`

3. **Redis connection error?**
   - Install Redis: `sudo apt-get install redis-server` (Linux) or `brew install redis` (Mac)
   - Start Redis: `redis-server`

## 📝 Key Files

- `config/` - Configuration files for each node type
- `src/` - Source code organized by component
- `deploy.sh` / `deploy.ps1` - Deployment scripts
- `test_system.py` - System test script

## 🎯 What You Get

This system demonstrates:

- ✅ Distributed transactions (2PC)
- ✅ Fault tolerance (crash, omission, Byzantine)
- ✅ Load balancing
- ✅ Data replication
- ✅ Performance monitoring
- ✅ Web GUI dashboard

All requirements from TIE Assignment 2 are met!

## 💡 Next Steps

1. Explore the GUI dashboard at http://localhost:8080
2. Review the architecture diagrams
3. Customize configuration files
4. Add your business logic
5. Deploy to production

Happy coding! 🎉
