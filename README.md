# InfraMon

**Docker Container Monitoring and Management System**

![Dashboard](assets/Dashboard.png)

## Overview

InfraMon is a comprehensive infrastructure monitoring and management application designed to provide real-time visibility into Docker containerized environments. The application enables system administrators and DevOps engineers to monitor, manage, and analyze Docker containers running on host machines through an intuitive, modern web interface.

The system bridges the gap between container management and system monitoring, offering a seamless experience for controlling your container infrastructure.

## Key Features

### 🚀 Real-time Container Monitoring
Display all Docker containers running on the host machine with their current state, resource utilization, and health status in real-time.

### 🔄 Container Lifecycle Management
Full control over your containers:
- **Start/Stop/Restart**: Manage container state directly from the UI.
- **Kill/Remove**: Forcefully stop or remove containers.
- **Pause/Unpause**: Temporarily freeze container processes.

### 🐳 Docker Compose Integration
- Automatically detects `docker-compose.yaml` files.
- Visualizes compose projects and services.
- Supports image updates via `docker compose pull`.

### 🔍 Deep Inspection & Shell Access
- **Comprehensive Inspection**: View full container configuration, network settings, volume mounts, and environment variables.
- **Web Terminal**: interactive shell access (`/bin/sh` or `/bin/bash`) directly in your browser via WebSocket.

### 📊 Resource Analytics
- **System Monitoring**: Track host machine resources including CPU, memory, disk usage, and network statistics.
- **Container Analytics**: Real-time charts for container-level resource consumption (CPU, Memory, Network I/O, Block I/O).

### 📝 Centralized Logging
- View real-time streaming logs for any container.
- Search, filter, and download logs.
- Support for ANSI colors and timestamp toggles.

### 🎨 Modern User Experience
- Responsive, accessible interface built with React and Tailwind CSS.
- **Dark/Light Mode**: Fully supported theme switching.
- **Group Management**: Organize containers into logical groups for easier management.

## Screenshots

### Container Management
Manage all your containers with advanced filtering and bulk actions.
![Containers](assets/Containers.png)

### Detailed Inspection
Deep dive into container configuration and status.
![Container Info](assets/Container_Info.png)

### Real-time Statistics
Monitor resource usage with interactive charts.
![Container Stats](assets/Container_Stats.png)

### Live Logs
Stream and search container logs in real-time.
![Container Logs](assets/Container_Logs.png)

## Technical Architecture

The application follows a modern three-tier architecture:

- **Frontend**: React 18+ with TypeScript, Tailwind CSS 4, and React Router.
- **Backend**: Python FastAPI providing RESTful APIs with async/await support.
- **Database**: SQLite database managed through Alembic ORM.
- **Infrastructure**: Fully containerized with Docker and orchestrated via Docker Compose.

## Quick Start

### Prerequisites

- Docker Engine 24.0+
- Docker Compose v2.24+
- Git

### Installation

1. Clone the repository:
```bash
git clone https://git.cib-digital.tech/InfraMon.git
cd InfraMon
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:
```bash
SECRET_KEY=your-super-secret-key
ADMIN_PASSWORD=your-strong-password
```

4. Start the application:
```bash
make up
```

5. Access the application:
- Web UI: http://localhost:3005
- API Docs: http://localhost:8065/api/docs

## Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm or yarn

### Backend Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Start development server
make dev-backend
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

## Project Structure

```
InfraMon/
├── backend/              # FastAPI backend
│   ├── app/             # Application code
│   │   ├── api/        # API routes
│   │   ├── core/       # Configuration
│   │   ├── db/         # Database
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic schemas
│   │   └── services/   # Business logic
│   ├── tests/          # Unit tests
│   └── alembic/        # Database migrations
├── frontend/            # React frontend
│   ├── src/            # Source code
│   │   ├── components/ # React components
│   │   ├── hooks/      # Custom hooks
│   │   ├── pages/      # Page components
│   │   └── services/   # API services
│   └── tests/          # Tests
├── docker/             # Docker configurations
└── docs/               # Documentation
```

## API Documentation

API documentation is available at `/api/docs` when running the backend server.

### Main Endpoints

- `GET /api/v1/containers` - List containers
- `POST /api/v1/containers/{id}/start` - Start container
- `POST /api/v1/containers/{id}/stop` - Stop container
- `POST /api/v1/containers/{id}/restart` - Restart container
- `GET /api/v1/containers/{id}/logs` - Get container logs
- `GET /api/v1/stats/dashboard` - Get dashboard statistics

## Testing

```bash
# Run all tests
make test

# Run backend tests
make test-backend

# Run frontend tests
make test-frontend
```

## Building for Production

```bash
make build
make up
```

## License

MIT License
