# InfraMon

Docker Container Monitoring and Management System

## Overview

InfraMon is a comprehensive infrastructure monitoring and management application designed to provide real-time visibility into Docker containerized environments.

## Features

- Real-time container monitoring
- Container lifecycle management (start, stop, restart)
- Docker Compose integration
- System resource monitoring (CPU, Memory, Disk)
- Modern web interface with dark/light theme
- OAuth 2.0 authentication

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
- Web UI: http://localhost:3000
- API Docs: http://localhost:8000/api/docs

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## License

MIT License
