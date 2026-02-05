# InfraMon Architecture Documentation

**Document Version:** 1.0  
**Last Updated:** February 2026

---

## 1. System Overview

InfraMon is a full-stack Docker container monitoring and management application built with a modern, asynchronous architecture.

```mermaid
flowchart TB
    subgraph User["User Layer"]
        Browser["Web Browser"]
        Mobile["Mobile Device"]
    end

    subgraph Frontend["Frontend Layer"]
        React["React SPA"]
        Vite["Vite Build Tool"]
        Tailwind["Tailwind CSS"]
        Zustand["Zustand State"]
        ReactQuery["TanStack Query"]
    end

    subgraph Backend["Backend Layer"]
        FastAPI["FastAPI Server"]
        Auth["Authentication"]
        API["REST API"]
        Services["Business Logic"]
    end

    subgraph Data["Data Layer"]
        SQLite["SQLite Database"]
        Alembic["Alembic Migrations"]
    end

    subgraph Runtime["Container Runtime"]
        Docker["Docker/Podman/Colima"]
        Containers["Docker Containers"]
    end

    Browser --> React
    React --> Vite
    React --> Tailwind
    React --> Zustand
    React --> ReactQuery

    React <-->|HTTP/REST| FastAPI
    FastAPI --> Auth
    FastAPI --> API
    FastAPI --> Services

    Services --> SQLite
    SQLite --> Alembic

    Services --> Docker
    Docker --> Containers

    classDef primary fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef secondary fill:#10b981,stroke:#059669,color:#fff
    classDef tertiary fill:#6366f1,stroke:#4f46e5,color:#fff

    class Frontend,React secondary
    class Backend,FastAPI primary
    class Data,Runtime tertiary
```

---

## 2. Backend Architecture

The backend follows a layered architecture pattern with clear separation of concerns.

```mermaid
flowchart LR
    subgraph Client["Client"]
        HTTP["HTTP Requests"]
    end

    subgraph API["API Layer"]
        FastAPI["FastAPI Framework"]
        Routes["API Routes"]
        Validators["Pydantic Validators"]
    end

    subgraph Service["Service Layer"]
        AuthService["Authentication Service"]
        ContainerService["Container Service"]
        StatsService["Stats Service"]
        GroupService["Group Service"]
    end

    subgraph Data["Data Layer"]
        Models["SQLAlchemy Models"]
        Database["Database Connection"]
        Repositories["Repositories"]
    end

    subgraph External["External Services"]
        DockerSDK["Docker SDK"]
        System["System Metrics (psutil)"]
    end

    HTTP --> FastAPI
    FastAPI --> Routes
    Routes --> Validators
    Validators --> AuthService
    Validators --> ContainerService
    Validators --> StatsService
    Validators --> GroupService

    AuthService --> Models
    ContainerService --> Models
    StatsService --> Models
    GroupService --> Models

    Models --> Database
    Database --> Repositories

    ContainerService --> DockerSDK
    StatsService --> System

    classDef layer fill:#1e293b,stroke:#475569,color:#fff
    classDef service fill:#059669,stroke:#047857,color:#fff
    classDef external fill:#7c3aed,stroke:#5b21b6,color:#fff

    class API,Service,Data layer
    class AuthService,ContainerService,StatsService,GroupService service
    class DockerSDK,System external
```

### Backend Directory Structure

```
backend/
├── app/
│   ├── api/v1/              # API endpoints
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── containers.py    # Container management
│   │   ├── stats.py         # Statistics endpoints
│   │   ├── groups.py        # Container groups
│   │   └── users.py         # User management
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings
│   │   ├── security.py      # Security middleware
│   │   └── ...
│   ├── db/                   # Database layer
│   │   ├── database.py       # Database connection
│   │   └── ...
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── container.py
│   │   └── container_group.py
│   ├── services/           # Business logic
│   │   ├── docker_service.py
│   │   ├── container_service.py
│   │   ├── stats_service.py
│   │   └── metrics_collector.py
│   └── main.py             # Application entry
├── tests/                  # Test suite
└── requirements.txt
```

---

## 3. Frontend Architecture

The frontend uses a component-based architecture with centralized state management.

```mermaid
flowchart TB
    subgraph App["React Application"]
        subgraph Router["React Router"]
            Routes["Route Definitions"]
            Protected["Protected Routes"]
        end

        subgraph State["State Management"]
            Zustand["Zustand Store"]
            TanStack["TanStack Query"]
            Context["React Context"]
        end

        subgraph Components["UI Components"]
            Layout["Layout Components"]
            Common["Common Components"]
            Pages["Page Components"]
        end

        subgraph API["API Layer"]
            Axios["Axios Client"]
            Interceptors["Request/Response Interceptors"]
            Services["API Services"]
        end

        subgraph Hooks["Custom Hooks"]
            Auth["useAuth"]
            Theme["useTheme"]
            Data["useRealTimeData"]
        end
    end

    Routes --> Protected
    Protected --> Components
    Components --> Layout
    Components --> Common
    Components --> Pages

    Components --> State
    State --> Zustand
    State --> TanStack
    State --> Context

    Pages --> Hooks
    Hooks --> Auth
    Hooks --> Theme
    Hooks --> Data

    Hooks --> API
    API --> Axios
    Axios --> Interceptors
    Interceptors --> Services

    classDef primary fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef secondary fill:#10b981,stroke:#059669,color:#fff
    classDef tertiary fill:#6366f1,stroke:#4f46e5,color:#fff

    class Router,Components,API,Hooks primary
    class State,Services secondary
    class App,Routes tertiary
```

### Frontend Directory Structure

```
frontend/
├── src/
│   ├── api/                  # API definitions
│   │   └── endpoints.ts
│   ├── components/           # React components
│   │   ├── common/           # Shared components
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   └── ThemeToggle/
│   │   ├── layout/           # Layout components
│   │   │   ├── Sidebar/
│   │   │   ├── Header/
│   │   │   └── Layout/
│   │   └── pages/            # Page components
│   │       ├── Login/
│   │       ├── Dashboard/
│   │       ├── Containers/
│   │       └── Settings/
│   ├── hooks/                # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useTheme.ts
│   │   └── useRealTimeData.ts
│   ├── services/             # API services
│   │   └── api.ts
│   ├── store/                # State management
│   │   └── useStore.ts
│   ├── types/                # TypeScript types
│   │   └── index.ts
│   ├── utils/                # Utilities
│   │   └── helpers.ts
│   └── test/                 # Test setup
└── package.json
```

---

## 4. Data Flow

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Database
    participant Docker

    User->>Frontend: Enter credentials
    Frontend->>API: POST /auth/login
    API->>Database: Verify user
    Database-->>API: User data
    API->>API: Validate password (bcrypt)
    API->>API: Generate JWT tokens
    API-->>Frontend: { access_token, refresh_token, user }
    Frontend->>Frontend: Store tokens

    Note over Frontend,API: Subsequent requests include Bearer token
    Frontend->>API: GET /containers (with Authorization header)
    API->>API: Verify JWT token
    API-->>Frontend: Container data
```

### Container Management Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant DockerSDK
    participant Docker

    User->>Frontend: Click "Start Container"
    Frontend->>Backend: POST /containers/{id}/start
    Backend->>Backend: Validate request
    Backend->>DockerSDK: client.containers.get(id)
    DockerSDK->>Docker: API call
    Docker-->>DockerSDK: Container response
    DockerSDK-->>Backend: Container object
    Backend->>Backend: Format response
    Backend-->>Frontend: { success: true }
    Frontend->>Frontend: Update UI
    Frontend->>Backend: GET /containers/{id}/stats
    Backend->>DockerSDK: Get container stats
    DockerSDK-->>Backend: Stats data
    Backend-->>Frontend: Real-time statistics
```

### Real-Time Data Flow

```mermaid
flowchart LR
    subgraph Collector["Metrics Collector"]
        Timer["Timer"]
        Gather["Gather Metrics"]
    end

    subgraph Cache["Cache Layer"]
        Memory["In-Memory Cache"]
    end

    subgraph API["API Layer"]
        Endpoint["Stats Endpoint"]
        Query["Query Handler"]
    end

    subgraph Frontend["Frontend"]
        ReactQuery["TanStack Query"]
        Recharts["Recharts Charts"]
        UI["Dashboard UI"]
    end

    Timer -->|interval| Gather
    Gather --> Docker
    Gather --> System
    Docker --> Memory
    System --> Memory

    Memory --> Endpoint
    Endpoint --> Query

    Query --> ReactQuery
    ReactQuery --> Recharts
    Recharts --> UI

    classDef process fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef storage fill:#10b981,stroke:#059669,color:#fff
    classDef external fill:#6366f1,stroke:#5b21b6,color:#fff

    class Collector,API,Frontend process
    class Cache,Memory storage
    class Docker,System external
```

---

## 5. Database Schema

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string email UK
        string hashed_password
        boolean is_active
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }

    CONTAINERS {
        int id PK
        string container_id UK
        string name
        string image
        string status
        string compose_file
        json labels
        json ports
        datetime created_at
        datetime updated_at
    }

    CONTAINER_GROUPS {
        int id PK
        string name UK
        string description
        string color
        datetime created_at
        datetime updated_at
    }

    CONTAINER_2_GROUP {
        int container_id FK
        int group_id FK
    }

    USERS ||--o{ CONTAINERS : manages
    CONTAINERS }o--|| CONTAINER_2_GROUP : belongs_to
    CONTAINER_GROUPS }o--|| CONTAINER_2_GROUP : contains
```

---

## 6. Deployment Architecture

### Development Environment

```mermaid
flowchart TB
    subgraph Host["Developer Machine"]
        Browser["Browser\nlocalhost:9876"]
        BackendDev["Backend Dev\nlocalhost:8000"]
        FrontendDev["Frontend Dev\nlocalhost:3000"]
        Vite["Vite HMR"]
    end

    subgraph Docker["Docker Runtime"]
        DockerSocket["Docker Socket\n/var/run/docker.sock"]
        TargetContainers["Target Containers"]
    end

    Browser <-->|Vite Proxy| FrontendDev
    FrontendDev <-->|HTTP| BackendDev
    BackendDev <--> DockerSocket
    DockerSocket --> TargetContainers

    classDef local fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef docker fill:#10b981,stroke:#059669,color:#fff

    class Host,BackendDev,FrontendDev local
    class Docker,DockerSocket,TargetContainers docker
```

### Production Environment

```mermaid
flowchart TB
    subgraph Internet["Internet"]
        Users["Users\nHTTPS"]
        CDN["CDN\nStatic Assets"]
    end

    subgraph Server["Production Server"]
        Nginx["Nginx\nReverse Proxy"]
        Backend["Backend\nGunicorn + Uvicorn"]
        Frontend["Frontend\nNginx Static"]
        Monitor["Health Check"]
    end

    subgraph Data["Data Layer"]
        Volume["Docker Volume\nSQLite DB"]
    end

    subgraph Runtime["Container Runtime"]
        DockerSocket["Docker Socket"]
        TargetContainers["Target Containers"]
    end

    Users -->|HTTPS| Nginx
    Nginx -->|/api| Backend
    Nginx -->|/| Frontend
    CDN --> Nginx

    Backend --> Volume
    Backend --> DockerSocket
    DockerSocket --> TargetContainers
    Monitor -.->|Health Check| Backend

    classDef server fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef container fill:#10b981,stroke:#059669,color:#fff
    classDef external fill:#6366f1,stroke:#5b21b6,color:#fff

    class Server,Nginx,Backend,Frontend,Monitor server
    class Data,Runtime,Volume container
    class Internet,Users,CDN external
```

---

## 7. Security Architecture

```mermaid
flowchart TB
    subgraph Request["Incoming Request"]
        HTTPS["HTTPS/TLS"]
        Headers["Request Headers"]
        Body["Request Body"]
    end

    subgraph Middleware["Middleware Stack"]
        CORS["CORS Middleware"]
        RateLimit["Rate Limiting"]
        Sanitize["Input Sanitization"]
        SecurityHeaders["Security Headers"]
        Auth["JWT Authentication"]
    end

    subgraph API["API Layer"]
        Routes["API Routes"]
        Validators["Pydantic Models"]
        Handlers["Request Handlers"]
    end

    subgraph Response["Response"]
        JSON["JSON Response"]
        Security["Security Headers"]
        Status["Status Code"]
    end

    Request --> HTTPS
    HTTPS --> CORS
    CORS --> RateLimit
    RateLimit --> Sanitize
    Sanitize --> SecurityHeaders
    SecurityHeaders --> Auth
    Auth --> Routes
    Routes --> Validators
    Validators --> Handlers
    Handlers --> Response

    classDef middleware fill:#7c3aed,stroke:#5b21b6,color:#fff
    classDef layer fill:#1e293b,stroke:#475569,color:#fff

    class Middleware middleware
    class Request,API,Response layer
```

---

## 8. Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 18 + TypeScript | UI framework |
| **Build Tool** | Vite 5 | Development & production build |
| **Styling** | Tailwind CSS 4 | Utility-first styling |
| **State** | Zustand 4 | Global client state |
| **Data Fetching** | TanStack Query 5 | Server state management |
| **Routing** | React Router 6 | Client-side routing |
| **HTTP Client** | Axios | HTTP requests |
| **Backend** | FastAPI + Python 3.11 | REST API framework |
| **Database** | SQLite + SQLAlchemy 2.0 | Data persistence |
| **ORM** | Alembic | Database migrations |
| **Container SDK** | Docker Python SDK | Container management |
| **Authentication** | python-jose + passlib | JWT + bcrypt |
| **Validation** | Pydantic 2 | Data validation |
| **Testing** | pytest + Vitest | Unit & integration tests |
| **CI/CD** | GitHub Actions | Automated pipeline |
| **Deployment** | Docker Compose | Container orchestration |

---

## 9. Key Design Decisions

### Why This Architecture?

1. **FastAPI + Async Python**
   - Native async support for concurrent container operations
   - Automatic API documentation (OpenAPI)
   - High performance (on par with Node.js)

2. **React + TypeScript**
   - Type safety across full stack
   - Large ecosystem and community
   - Excellent developer experience

3. **SQLite + SQLAlchemy**
   - Zero-configuration database
   - ACID compliance
   - Easy backups (single file)

4. **Docker SDK for Python**
   - Direct container management without CLI
   - Full Docker API access
   - Multi-runtime support (Docker/Podman/Colima)

5. **JWT Authentication**
   - Stateless sessions
   - Configurable expiration
   - Refresh token rotation

---

## 10. Performance Considerations

```mermaid
flowchart LR
    subgraph Optimizations["Optimization Strategies"]
        Caching["Request Caching\n(TanStack Query)"]
        Compression["Gzip Compression\n(Nginx)"]
        Chunking["Code Splitting\n(Vite)"]
        Polling["Smart Polling\n(5s interval)"]
        Debouncing["Debounced Inputs\n(User actions)"]
    end

    subgraph Metrics["Performance Metrics"]
        FCP["First Contentful Paint\n< 1s"]
        LCP["Largest Contentful Paint\n< 2.5s"]
        TTFB["Time to First Byte\n< 200ms"]
        TTI["Time to Interactive\n< 3s"]
    end

    Optimizations --> Metrics

    classDef opt fill:#3b82f6,stroke:#1d4ed8,color:#fff
    classDef metric fill:#10b981,stroke:#059669,color:#fff

    class Optimizations opt
    class Metrics metric
```

---

*Document generated for InfraMon v0.1.0*
