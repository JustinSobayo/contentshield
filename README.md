# Content Shield

Content Shield is a web app that helps creators check a video for social platform policy risk before posting it.

## The Problem It Solves

If you post a video without reviewing it carefully, you can run into:

- platform takedowns
- limited reach or demonetization
- missed policy issues in the audio, visuals, or on-screen text
- uncertainty about whether a video is risky enough to rewrite or re-edit

Content Shield is built to make that first review faster. You upload a video, choose the platform, and get a simple risk assessment with flagged issues and a short explanation.

## What The App Does

- lets you choose a target platform: YouTube, TikTok, Instagram, or X
- uploads a video to the backend for analysis
- uses Gemini to review the video
- pulls platform policy context from local policy documents using retrieval
- returns a `Low`, `Medium`, or `High` risk level
- returns a short summary of why that risk level was assigned
- returns flagged issues with timestamps, snippets, and rationale

## How It Works

1. The React frontend lets the user pick a platform and upload a video.
2. The FastAPI backend accepts the file at `POST /analyze`.
3. The backend retrieves policy context from documents in `backend/policy_docs`.
4. Gemini analyzes the uploaded video with that policy context.
5. The app returns a structured result for the frontend to display.

## Stack

- frontend: React, Vite, TypeScript, Tailwind
- backend: FastAPI
- AI: Google Gemini
- retrieval: LlamaIndex + ChromaDB
- caching and rate limiting: Redis

## Run With Docker

Docker is the easiest way to run the full project because it starts the frontend, backend, and Redis together.

### 1. Create the backend env file

Copy `backend/env.example` to `backend/.env` and add your Gemini key:

```env
GEMINI_API_KEY=your_api_key_here
```

### 2. Start the app

```bash
docker compose up --build
```

### 3. Open the app

- frontend: `http://localhost:8080`
- backend docs: `http://localhost:8000/docs`

## Run Without Docker

Use this if you want to run the frontend and backend yourself.

### Requirements

- Python 3.10+
- Node.js 20+
- Redis
- FFmpeg

### 1. Backend setup

Make sure Redis is running locally, then create `backend/.env` and add your Gemini key. Set `REDIS_URL` to your local Redis instance.

Example:

```env
GEMINI_API_KEY=your_api_key_here
REDIS_URL=redis://localhost:6379/0
```

Install backend dependencies:

```bash
cd backend
python -m venv venv
```

Activate the virtual environment, then install packages:

```bash
pip install -r requirements.txt
```

Start the backend from the `backend` folder:

```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend setup

From the project root:

```bash
npm ci
npm run dev -- --port 8080
```

Open `http://localhost:8080`.

## Project Notes

- policy documents are stored in `backend/policy_docs`
- the local vector database is stored in `backend/chroma_db`
- Redis is used for caching analysis results and rate limiting
- the frontend defaults to `http://localhost:8000` for the API if `VITE_API_URL` is not set
