# Content Shield

A video content analysis platform powered by AI.

## 🚀 Quick Start (Docker) - Recommended

The easiest way to run Content Shield is using Docker. This ensures all dependencies (like FFmpeg and Python libraries) are installed automatically.

### Prerequisites
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### 1. Setup Environment
Create the backend environment file and add your API key:

```bash
cp backend/env.example backend/.env
# Open backend/.env on your computer and paste your GEMINI_API_KEY inside
```

### 2. Run the App
Start the application containers:

```bash
docker compose up --build
```
*(The first run may take a few minutes to download dependencies. subsequent runs will be instant.)*

### 3. Access
*   **Web App**: [http://localhost:8080](http://localhost:8080)
*   **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Manual Setup (No Docker)

If you prefer to run dependencies on your host machine directly.

### 1. Backend Setup
Requires **Python 3.10+** and **FFmpeg** installed on your system.

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables
```bash
cp backend/env.example backend/.env
# Edit backend/.env and add your GEMINI_API_KEY
```

### 3. Frontend Setup
Requires **Node.js 20+**.

```bash
npm install
```

### 4. Running Locally
You can start both servers with the helper script:

```bash
chmod +x start_dev.sh
./start_dev.sh
```

Or run them manually:

**Backend:**
```bash
source backend/venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
npm run dev
```

Open [http://localhost:8080](http://localhost:8080) in your browser.
