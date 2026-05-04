# Redis Setup with WSL (Windows Subsystem for Linux)

## Step 1: Install WSL

### Option A: Automatic Installation (Easiest)
Open PowerShell as Administrator and run:
```powershell
wsl --install
```

This will:
- Enable WSL2
- Install Ubuntu Linux (default)
- Set up the subsystem
- Prompt you to create a username and password when first launched

**Note:** You may need to restart your computer after installation.

### Option B: Manual Installation
1. Open PowerShell as Administrator
2. Run: `wsl --install -d Ubuntu`
3. After installation completes, restart Windows
4. Launch Ubuntu from Start menu and complete setup

---

## Step 2: Verify WSL Installation

After installation and restart, run in PowerShell:
```powershell
wsl -l -v
```

You should see:
```
  NAME            STATE           VERSION
* Ubuntu          Running         2
```

---

## Step 3: Install Redis in WSL

Once WSL is installed, open Ubuntu terminal and run these commands:

### In WSL/Ubuntu Terminal:
```bash
# Update package lists
sudo apt-get update

# Install Redis
sudo apt-get install -y redis-server

# Verify installation
redis-cli --version
```

---

## Step 4: Start Redis

You can start Redis in two ways:

### Option A: Start Redis in Background (Recommended)
In WSL/Ubuntu terminal:
```bash
sudo service redis-server start

# Verify it's running
sudo service redis-server status
```

### Option B: Start Redis in Foreground (For Debugging)
```bash
redis-server
```
You'll see output like:
```
* Ready to accept connections
```

---

## Step 5: Test Redis Connection from Windows

Open PowerShell and run:
```powershell
cd 'c:\Users\prana\Capstone_Intelligent_Job_Searching'
& .\.venv\Scripts\Activate.ps1
python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); print('✓ Redis is running!' if r.ping() else '✗ Redis failed')"
```

Expected output: `✓ Redis is running!`

---

## Step 6: (Optional) Configure Redis to Auto-Start

To have Redis start automatically when you log in:

### In WSL/Ubuntu Terminal:
```bash
# Edit sudoers to allow redis-server to start without password
sudo visudo

# Add this line at the end:
# <yourusername> ALL = NOPASSWD: /etc/init.d/redis-server

# Then create a startup script
echo "sudo service redis-server start" >> ~/.bashrc
```

---

## Step 7: Quick Start Guide for Daily Use

### Starting Redis (Do This Every Day You Use The Application)

**Option 1: Using WSL Command from PowerShell (No Terminal Window)**
```powershell
wsl sudo service redis-server start
```

**Option 2: Keep WSL Terminal Open**
1. Open Ubuntu terminal
2. Run: `sudo service redis-server start`
3. Keep the terminal open
4. Use other PowerShell terminals for the app

**Option 3: Start in Background**
Open Ubuntu terminal and run:
```bash
sudo service redis-server start &
exit
```
This starts Redis and closes the WSL terminal.

---

## Verifying Everything is Ready

Run this from PowerShell after starting Redis:
```powershell
cd DB
& .\.venv\Scripts\Activate.ps1
python check_services.py
```

You should see:
```
✓ Redis is running on localhost:6379
✓ MongoDB is running
```

---

## Troubleshooting

### "command not found: redis-server"
- Redis not installed. Run: `sudo apt-get install -y redis-server`

### "Connection refused on localhost:6379"
- Redis is not running. Start it: `sudo service redis-server start`

### "Permission denied"
- You need sudo. Use: `sudo service redis-server start`

### WSL Not Found
- WSL not installed. Run: `wsl --install` in PowerShell (Admin)
- Restart your computer after installation

---

## Next Steps

Once Redis is running and verified:

1. Start the DB API server (Terminal 1)
2. Start the Worker (Terminal 2)
3. Start the WebServer (Terminal 3)
4. Visit http://localhost:5168

See [INTEGRATION_STATUS.md](INTEGRATION_STATUS.md) for the full startup guide.
