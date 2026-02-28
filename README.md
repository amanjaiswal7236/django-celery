# Django Celery Task Management Platform 🚀

A **production-ready full-stack platform** for managing asynchronous tasks with **real-time progress updates**, built using **Django, Celery, Redis, React, and Docker**.

---

## 📋 Project Overview

### 🔹 What This Project Does

This platform allows users to **create, manage, and monitor long-running background tasks** with live updates.

You can think of it as a **distributed job queue system with a modern UI**, where users can:

* Submit background tasks from a React frontend
* Track progress in real time (no page refresh)
* Monitor task lifecycle: **Pending → Running → Success / Failed**
* View detailed execution logs
* Retry failed tasks automatically or manually
* Analyze system-wide and user-specific metrics

---

## ⚙️ How It Works

### 🔁 Task Execution Flow

1. User creates a task → Frontend sends request to Django API
2. Django stores task → Status set to **Pending**
3. Task queued to **Celery** via **Redis**
4. Celery worker picks up task → Status **Running**
5. Task executes → Progress updates (0–100%)
6. Task finishes → **Success** or **Failed**
7. WebSocket pushes updates → UI updates instantly

---

### 🔴 Real-Time Updates

* Frontend connects to:

  ```
  ws://localhost:8000/ws/tasks/
  ```
* Backend sends updates when:

  * Task status changes
  * Progress percentage updates
  * Task completes or fails
* UI updates automatically via WebSockets (Django Channels)

---

## 🏗️ Architecture Overview

### Backend (Django)

* Django 4.2 + Django REST Framework
* WebSockets via Django Channels
* PostgreSQL (SQLite for dev)
* Custom User model + authentication

### Task Queue (Celery)

* Celery 5.3
* Redis as broker & result backend
* Parallel worker execution
* Celery Beat for scheduled jobs

### Frontend (React)

* React 18 with hooks
* Material-UI (MUI)
* WebSocket client
* Responsive dashboard

### Infrastructure (Docker)

* Fully containerized services
* Docker Compose orchestration
* Horizontally scalable workers

---

## ✨ Key Features

### ✅ Task Types

* **File Processing** – resize, convert, transform files
* **Web Scraping** – scrape data using CSS selectors
* **Report Generation** – generate Excel/PDF reports

### ✅ Real-Time Monitoring

* Live progress bars
* Instant task updates
* Streaming logs
* WebSocket-based communication

### ✅ Multi-User Support

* User authentication & authorization
* Workspace isolation
* Admin analytics dashboard
* CSRF + session security

### ✅ Error Handling

* Automatic retries (configurable)
* Detailed error logs
* Manual retry option
* Robust logging system

### ✅ Analytics

* User-level statistics
* Admin system metrics
* Task success/failure rates
* Task distribution insights

---

## 💼 Use Cases

* Background job processing
* Data pipelines & transformations
* Automated web scraping
* Report generation systems
* Team-based task workflows

---

## 🧠 Why This Project Is Resume-Ready

This project demonstrates:

* 🏗️ Distributed system design
* ⚡ Async processing with Celery
* 🔄 Real-time communication (WebSockets)
* 🐳 Docker & DevOps practices
* 🔐 Authentication & security
* 📊 Full-stack development
* 🗄️ Database modeling
* 🧪 Clean architecture & best practices

---

## 🧰 Tech Stack

| Layer    | Technology                |
| -------- | ------------------------- |
| Backend  | Django 4.2, DRF, Channels |
| Queue    | Celery 5.3, Redis         |
| Database | PostgreSQL / SQLite       |
| Frontend | React 18, Material-UI     |
| Realtime | WebSockets                |
| Infra    | Docker, Docker Compose    |

---

## 🚀 Quick Start

### Prerequisites

* Docker & Docker Compose
* Python 3.11+ (local dev)

---

### 🐳 Docker Setup (Recommended)

```bash
git clone <repository-url>
cd django-celery
```

```bash
cp .env.example .env
```

```bash
docker-compose up --build
```

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

**Access:**

* Frontend → [http://localhost:3000](http://localhost:3000)
* Backend → [http://localhost:8000](http://localhost:8000)
* Admin → [http://localhost:8000/admin](http://localhost:8000/admin)

---

### 💻 Local Development

#### Backend

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Redis

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

#### Celery Worker

```bash
celery -A config worker --loglevel=info
```

#### Celery Beat (optional)

```bash
celery -A config beat --loglevel=info
```

#### Frontend

```bash
cd frontend
npm install
npm start
```

---

## 📁 Project Structure

```
django-celery/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── asgi.py
├── accounts/
├── tasks/
│   ├── models.py
│   ├── tasks.py
│   ├── views.py
│   ├── consumers.py
│   └── routing.py
├── frontend/
│   └── src/
├── docker-compose.yml
├── Dockerfile.backend
└── requirements.txt
```

---

## 🔌 API Endpoints

### Authentication

* `POST /api/auth/register/`
* `POST /api/auth/login/`
* `POST /api/auth/logout/`
* `GET /api/auth/me/`

### Tasks

* `GET /api/tasks/`
* `POST /api/tasks/`
* `GET /api/tasks/{id}/`
* `POST /api/tasks/{id}/retry/`
* `GET /api/tasks/{id}/logs/`
* `GET /api/tasks/analytics/`

### Admin

* `GET /api/tasks/admin/analytics/`

---

## 🔴 WebSocket

**Endpoint**

```
ws://localhost:8000/ws/tasks/
```

**Subscribe**

```json
{ "type": "subscribe_task", "task_id": 1 }
```

**Unsubscribe**

```json
{ "type": "unsubscribe_task", "task_id": 1 }
```

**Updates**

```json
{ "type": "task_update", "task": {...} }
```

---

## 🧪 Development Commands

```bash
python manage.py test
python manage.py makemigrations
python manage.py migrate
docker-compose exec backend python manage.py shell
docker-compose logs -f celery-worker
```

---

## 🚀 Production Checklist

* `DEBUG=False`
* Proper `ALLOWED_HOSTS`
* PostgreSQL database
* Secure `SECRET_KEY`
* Static files via Nginx
* SSL/TLS for WebSockets
* Environment-based secrets

---

## 📄 License

MIT

---

## 🤝 Contributing

Pull Requests are welcome.
Feel free to improve features, docs, or performance.

---
