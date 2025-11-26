# Django Celery Task Management Platform

A full-stack platform for managing asynchronous tasks with real-time progress updates. Built with Django, Celery, Redis, React, and Docker.

## 📋 Project Overview

### What This Project Does

This is a **production-ready task management platform** that allows users to create, manage, and monitor long-running asynchronous tasks with real-time progress tracking. Think of it as a **distributed job queue system** with a beautiful web interface where users can:

- **Submit tasks** (file processing, web scraping, report generation) through a React frontend
- **Monitor progress** in real-time via WebSockets without refreshing the page
- **Track status** as tasks move through: Pending → Running → Success/Failed
- **View detailed logs** for each task execution
- **Retry failed tasks** with automatic retry mechanisms
- **Access analytics** dashboards for insights

### How It Works

#### Task Execution Flow:
1. **User creates a task** → Frontend sends POST request to Django API
2. **Django creates Task record** → Status set to "pending" in database
3. **Task queued to Celery** → Redis broker receives the task
4. **Celery worker picks up task** → Status changes to "running"
5. **Task executes** → Progress updates sent (0-100%)
6. **Task completes** → Status set to "success" or "failed"
7. **WebSocket sends update** → Frontend receives real-time notification

#### Real-Time Updates:
- Frontend connects to WebSocket endpoint (`ws://localhost:8000/ws/tasks/`)
- Users can subscribe to specific tasks for updates
- Backend pushes updates when:
  - Task status changes
  - Progress percentage updates
  - Task completes or fails
- Frontend automatically updates UI without page refresh

### Architecture Highlights

**Backend (Django)**:
- RESTful API with Django REST Framework
- WebSocket support via Django Channels
- PostgreSQL database for data persistence
- Custom User model with authentication

**Task Queue (Celery)**:
- Asynchronous task processing
- Redis as message broker and result backend
- Multiple workers can process tasks in parallel
- Celery Beat for scheduled task execution

**Frontend (React)**:
- Modern React 18 with hooks
- Material-UI for beautiful components
- Real-time WebSocket client
- Responsive dashboard design

**Infrastructure (Docker)**:
- All services containerized for easy deployment
- Orchestrated with Docker Compose
- Scalable architecture (add more workers as needed)

### Key Features

✅ **Three Task Types**:
- **File Processing**: Process files (resize, convert, transform)
- **Web Scraping**: Scrape data from websites using CSS selectors
- **Report Generation**: Generate Excel/PDF reports from data

✅ **Real-Time Monitoring**:
- Live progress bars
- Instant status updates
- Task logs streaming
- WebSocket-based communication

✅ **Multi-User Support**:
- User authentication and authorization
- Workspace isolation (users see only their tasks)
- Admin dashboard for system-wide analytics
- Session-based security with CSRF protection

✅ **Error Handling**:
- Automatic retry with configurable max retries
- Detailed error messages
- Manual retry option for failed tasks
- Comprehensive logging system

✅ **Analytics & Monitoring**:
- User dashboard with personal statistics
- Admin dashboard with system-wide metrics
- Task distribution charts
- Success rate tracking

### Use Cases

- **Background Job Processing**: Run long-running tasks without blocking the UI
- **Data Processing**: Batch file processing, data transformation pipelines
- **Web Scraping**: Automated data collection from websites
- **Report Generation**: Automated report creation and delivery
- **Multi-User Workflows**: Teams managing shared task queues

### Why This Project is Great for Your Resume

This project demonstrates:
- 🏗️ **System Design**: Distributed architecture with message queues
- ⚡ **Async Programming**: Celery for background task processing
- 🔄 **Real-Time Communication**: WebSockets for live updates
- 🐳 **DevOps**: Docker containerization and orchestration
- 🔐 **Security**: Authentication, CSRF protection, CORS handling
- 📊 **Full-Stack Development**: React frontend + Django backend
- 🗄️ **Database Design**: PostgreSQL with proper indexing
- 🧪 **Best Practices**: RESTful APIs, clean code structure

## Features

- ✅ **Task Management**: Create and manage tasks (file processing, web scraping, report generation)
- ✅ **Real-time Updates**: WebSocket-based live progress tracking
- ✅ **Status Tracking**: Monitor tasks from Pending → Running → Success/Fail
- ✅ **Task Logs**: View detailed logs for each task
- ✅ **Retry Mechanism**: Retry failed tasks with configurable max retries
- ✅ **Scheduling**: Schedule tasks for future execution
- ✅ **Multi-user Support**: User authentication and workspace isolation
- ✅ **Admin Dashboard**: Analytics and monitoring for administrators
- ✅ **Docker Support**: All services containerized for easy deployment

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework, Django Channels
- **Task Queue**: Celery 5.3 with Redis broker
- **Database**: PostgreSQL (or SQLite for development)
- **Frontend**: React 18 with Material-UI
- **Real-time**: WebSockets via Django Channels
- **Containerization**: Docker & Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd django-celery
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Build and start services**:
   ```bash
   docker-compose up --build
   ```

4. **Run migrations**:
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

5. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

### Local Development

1. **Backend Setup**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   ```

2. **Start Redis** (required for Celery):
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. **Start Django server**:
   ```bash
   python manage.py runserver
   ```

4. **Start Celery worker** (in another terminal):
   ```bash
   celery -A config worker --loglevel=info
   ```

5. **Start Celery beat** (optional, for scheduled tasks):
   ```bash
   celery -A config beat --loglevel=info
   ```

6. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Project Structure

```
django-celery/
├── config/              # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py       # Celery configuration
│   └── asgi.py         # ASGI config for WebSockets
├── accounts/            # User authentication app
├── tasks/               # Task management app
│   ├── models.py       # Task and TaskLog models
│   ├── tasks.py        # Celery task definitions
│   ├── views.py        # API views
│   ├── consumers.py    # WebSocket consumers
│   └── routing.py      # WebSocket routing
├── frontend/            # React application
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── services/   # API and WebSocket services
│   │   └── context/    # React context providers
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
└── requirements.txt
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `GET /api/auth/me/` - Get current user

### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Get task details
- `POST /api/tasks/{id}/retry/` - Retry failed task
- `GET /api/tasks/{id}/logs/` - Get task logs
- `GET /api/tasks/analytics/` - Get user analytics

### Admin
- `GET /api/tasks/admin/analytics/` - Admin analytics (staff only)

## WebSocket

Connect to `ws://localhost:8000/ws/tasks/` for real-time task updates.

**Messages**:
- Subscribe to task: `{"type": "subscribe_task", "task_id": 1}`
- Unsubscribe: `{"type": "unsubscribe_task", "task_id": 1}`

**Received Updates**:
- `{"type": "task_update", "task": {...}}`

## Task Types

1. **File Processing**: Process files (resize, convert, etc.)
   - Parameters: `file_path`, `operation`

2. **Web Scraping**: Scrape data from websites
   - Parameters: `url`, `selectors` (JSON object)

3. **Report Generation**: Generate reports (Excel, PDF, etc.)
   - Parameters: `report_type`, `data_source`

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing Django Shell
```bash
docker-compose exec backend python manage.py shell
```

### Viewing Celery Logs
```bash
docker-compose logs -f celery-worker
```

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure proper `ALLOWED_HOSTS`
3. Use PostgreSQL instead of SQLite
4. Set up proper secret key
5. Configure static file serving (nginx, etc.)
6. Use environment variables for sensitive data
7. Set up SSL/TLS for WebSocket connections

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

#   d j a n g o - c e l e r y  
 