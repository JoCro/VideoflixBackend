![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.x-green)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-DB-blue)
![Redis](https://img.shields.io/badge/Redis-Cache-red)
![FFmpeg](https://img.shields.io/badge/FFmpeg-HLS-orange)

# 🎬 VideoFlix -- Video Streaming Platform (Django + Docker + HLS)

VideoFlix is a full-stack streaming platform inspired by Netflix.\
It provides user authentication, secure JWT-based login with HttpOnly
cookies, email verification, password reset, and full HLS video
streaming with automatic background processing.

The entire backend runs inside **Docker containers** and can be started
with a single command using `docker-compose`.

---

## 📌 Features

### 🔐 Authentication System

- User registration with email confirmation\
- Login with JWT stored in **HttpOnly cookies**\
- Secure logout (refresh token blacklist)\
- Token refresh endpoint\
- Password reset via email (uid + token)\
- Fully working HTML email templates with embedded logo\
- Token expiration rules enforced (24 hours for password reset)

---

### 🎞️ Video Streaming (HLS)

- Videos uploaded via Django Admin
- Automatic HLS generation using **ffmpeg**
- Multi-resolution output:
  - **480p**
  - **720p**
  - **1080p**
- HLS served via:
  - Manifest endpoint\
    `/api/video/<movie_id>/<resolution>/index.m3u8`
  - Segment endpoint\
    `/api/video/<movie_id>/<resolution>/<segment>/`

---

### 🧵 Background Processing

Heavy workloads run asynchronously using:

- **Redis** (in-memory database)
- **Django RQ Worker**
- Queued ffmpeg tasks (HLS conversion)
- Automatic cleanup when videos are deleted

This ensures the Django server stays fast and responsive.

---

## 🐳 Dockerized Architecture

VideoFlix uses **docker-compose** to orchestrate:

Service Description

---

`videoflix_backend` Django + Gunicorn backend
`videoflix_database` PostgreSQL 18 database
`videoflix_redis` Redis server for caching & RQ
`rq-worker` (inside backend) Background video processing
Frontend (Live Server) Served manually outside Docker

All backend logic works entirely inside containers.

---

## 📦 Project Structure

    VideoFlix/
    │
    ├── videoflix_app/          # Django app
    │   ├── models.py           # Video model
    │   ├── services.py         # HLS generation logic
    │   ├── signals.py          # Auto-HLS on upload
    │   ├── api/                # DRF API
    │   ├── templates/          # Email templates
    │   └── ...
    │
    ├── media/
    │   ├── videos/             # Raw video uploads
    │   ├── thumbnails/         # Uploaded thumbnails
    │   └── hls/                # Generated HLS structures
    │
    ├── backend.Dockerfile      # Backend container
    ├── docker-compose.yml      # Full stack definition
    └── requirements.txt

---

## 🚀 Getting Started

### 1️⃣ Requirements

- Docker\
- Docker Compose\
- Optional: VS Code Live Server extension (for the frontend)

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/JoCro/VideoflixBackend.git
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 2️⃣ Create your .env file

- Duplicate the template: **cp .env.template .env**
- Edit fields as needed to your new **.env-file**

## ▶️ Start the entire backend with Docker

From the project root:

```bash
docker-compose up --build
```

This starts:

- Django backend on **http://127.0.0.1:8000**
- PostgreSQL database\
- Redis server\
- RQ worker inside backend container

---

## 🖥️ Frontend

The frontend is **not part of this repository**.\
It must be served via your local computer using a Live Server:

Example:

```text
http://127.0.0.1:5500/index.html
```

Email activation & password reset links point to this frontend.

---

## 🔑 API Overview

### ▶️ Authentication

Method Endpoint Description

---

POST `/api/register/` User signup
GET `/api/activate/?uid=...&token=...` Account activation
POST `/api/login/` Login (returns JWT in HttpOnly cookies)
POST `/api/logout/` Logout
POST `/api/token/refresh/` Refresh access token
POST `/api/password_reset/` Request password reset
POST `/api/password_confirm/<uid>/<token>/` Reset password

---

### ▶️ Video API

Method Endpoint Description

---

GET `/api/video/` List all available videos
GET `/api/video/<id>/<resolution>/index.m3u8` HLS manifest
GET `/api/video/<id>/<resolution>/<segment>/` TS segment file

---

## 🎥 How Video Upload & HLS Generation Works

1.  Admin uploads a video through Django Admin\
2.  Django saves the file in `media/videos/`\
3.  A `post_save` signal triggers\
4.  The video ID is added to a **Redis Queue**\
5.  The **RQ worker** runs ffmpeg:
    - Creates 480p, 720p, 1080p folders\
    - Generates `.ts` segments\
    - Generates `index.m3u8`\
6.  API immediately serves the video once HLS files are ready

No blocking, no server freezes --- production-grade workflow.

---

## ❗Troubleshooting

### 🔸 HLS returns 404

The video is still processing --- wait a few seconds.\
Check logs inside the backend container:

```bash
docker logs videoflix_backend
```

### 🔸 ffmpeg errors

Ensure your video file is a valid `.mp4`.

### 🔸 Emails not received

Check your SMTP settings inside Django.

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 🙌 Acknowledgements

Built with: - Django - DRF - Redis - Django RQ - ffmpeg - Docker -
Developer Akademie learning program

---

# 🎉 Enjoy Streaming with VideoFlix!
