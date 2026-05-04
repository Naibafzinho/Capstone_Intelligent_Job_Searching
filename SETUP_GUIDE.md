# JobRush Complete Setup Guide

## Prerequisites

Before starting the application, you need to have the following services running:
1. **MongoDB** - Database for storing users, resumes, jobs, and matches
2. **Redis** - In-memory queue for background processing

## Option 1: Using MongoDB Atlas (Cloud - Recommended for Development)

### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free account and log in
3. Create a new cluster (free tier available)
4. Create a database user with username and password
5. Get your connection string

### Step 2: Configure Connection String
1. Copy your MongoDB Atlas connection string
2. Update the `MONGODB_URI` in `.env` file:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster0.mongodb.net/TestDB
   ```
3. Replace `username`, `password`, and `cluster0` with your actual values

### Step 3: Redis
For development, you can use a free Redis cloud service:
1. Go to [Redis Cloud](https://redis.com/try-free/)
2. Create a free database
3. Note the host and port

**Alternative (Simpler for Local Testing):**
Use WSL (Windows Subsystem for Linux) or Docker to run Redis locally.

---

## Option 2: Using Local Services with Windows Subsystem for Linux (WSL)

### Prerequisites
- Windows 10/11 with WSL2 installed

### Step 1: Install MongoDB in WSL
```bash
# In WSL terminal
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

### Step 2: Install Redis in WSL
```bash
# In WSL terminal
sudo apt-get install -y redis-server
sudo service redis-server start
```

### Step 3: Keep WSL Services Running
Create a PowerShell script to start WSL services when needed:
```powershell
# wsl-start-services.ps1
wsl sudo service mongod start
wsl sudo service redis-server start
wsl sudo mongod --logpath /var/log/mongodb/mongod.log --fork
```

### Step 4: Update .env
```
MONGODB_URI=mongodb://localhost:27017/TestDB
```

---

## Quick Start Checklist

- [ ] MongoDB is running and accessible
- [ ] Redis is running on port 6379
- [ ] `.env` file configured with MONGODB_URI
- [ ] Python virtual environment created and activated
- [ ] Dependencies installed for all modules

## Running the Application

### Terminal 1: Start DB API Server
```powershell
cd DB
& .\.venv\Scripts\Activate.ps1
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Terminal 2: Start Worker (processes background jobs)
```powershell
cd DB
& .\.venv\Scripts\Activate.ps1
python worker.py
```

### Terminal 3: Start WebServer
```powershell
cd WebServer
dotnet watch run
```

The application will be available at: **http://localhost:5168**

---

## Testing the Integration

1. Navigate to http://localhost:5168
2. Click "Sign up"
3. Enter a new username, email, and password
4. You should see success message and be redirected to the home page

**If you see "Username already in use" with a new username:**
- Check that the DB API is running (Terminal 1)
- Check that the worker is running (Terminal 2)
- Check that MongoDB has the database ready
- Check the browser console for errors

---

## Troubleshooting

### "Connection refused" error
- Verify MongoDB is running
- Verify Redis is running on port 6379
- Check the MONGODB_URI in .env file

### "Username already in use" with new username
- MongoDB might have old test data
- Use MongoDB Compass to inspect and clear the Users collection
- Or restart fresh with a new MongoDB database

### API call timeouts
- Ensure worker.py is running in Terminal 2
- Check for errors in the worker terminal
- Verify database health with: `python -c "from DB_Management import DBManagement; db = DBManagement(); print(db.client.admin.command('ping'))"`
