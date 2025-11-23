# Content Shield

A video content analysis platform powered by AI.

## Setup

1.  **Backend Setup**
    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Create a `.env` file in the `backend/` directory:
    ```bash
    cp backend/env.example backend/.env
    ```
    Then edit `backend/.env` and add your `GEMINI_API_KEY`.

3.  **Frontend Setup**
    ```bash
    npm install
    ```

## Running Locally

You can start both servers with the helper script:

```bash
chmod +x start_dev.sh
./start_dev.sh
```

Or run them manually:

**Backend:**
```bash
source backend/venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000
```

**Frontend:**
```bash
npm run dev
```

Open [http://localhost:8080](http://localhost:8080) in your browser.
