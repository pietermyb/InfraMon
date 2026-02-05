#!/bin/bash

# InfraMon Deployment Script
# Supports development, staging, and production deployments with rolling updates

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
COMPOSE_OVERRIDE="${COMPOSE_OVERRIDE:-docker-compose.override.yml}"
ENV_FILE="${ENV_FILE:-.env}"

# Colors functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    if [ ! -f "$ENV_FILE" ]; then
        log_warning "Environment file $ENV_FILE not found"
        log_info "Creating from example..."
        if [ -f ".env.example" ]; then
            cp .env.example "$ENV_FILE"
            log_success "Created $ENV_FILE from .env.example"
            log_warning "Please configure $ENV_FILE with your settings"
        else
            log_error ".env.example not found"
            exit 1
        fi
    fi

    log_success "Prerequisites check passed"
}

# Pull latest images
pull_images() {
    log_info "Pulling latest images..."
    if docker compose -f "$COMPOSE_FILE" pull 2>/dev/null; then
        docker compose -f "$COMPOSE_FILE" pull
    elif docker-compose -f "$COMPOSE_FILE" pull; then
        docker-compose -f "$COMPOSE_FILE" pull
    fi
    log_success "Images pulled"
}

# Build images
build_images() {
    log_info "Building images..."
    if docker compose -f "$COMPOSE_FILE" build 2>/dev/null; then
        docker compose -f "$COMPOSE_FILE" build --no-cache
    elif docker-compose -f "$COMPOSE_FILE" build --no-cache; then
        docker-compose -f "$COMPOSE_FILE" build --no-cache
    fi
    log_success "Images built"
}

# Database migration
run_migrations() {
    log_info "Running database migrations..."
    docker compose -f "$COMPOSE_FILE" exec -T backend python -m alembic upgrade head
    log_success "Database migrations completed"
}

# Health check
health_check() {
    local max_attempts="${1:-30}"
    local attempt=1

    log_info "Waiting for services to be healthy..."

    while [ $attempt -le $max_attempts ]; do
        if curl -sf http://localhost:8065/health > /dev/null 2>&1; then
            log_success "Backend is healthy"
            return 0
        fi
        log_info "Attempt $attempt/$max_attempts: Backend not ready yet..."
        sleep 2
        ((attempt++))
    done

    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Rolling update for production
rolling_update() {
    log_info "Starting rolling update..."

    local services=("backend" "frontend")

    for service in "${services[@]}"; do
        log_info "Updating $service..."

        # Pull latest image
        docker compose -f "$COMPOSE_FILE" pull "$service"

        # Recreate service with health check
        docker compose -f "$COMPOSE_FILE" up -d "$service"

        # Wait for health check
        if ! health_check 60; then
            log_error "Rolling update failed for $service"
            docker compose -f "$COMPOSE_FILE" logs "$service"
            exit 1
        fi

        log_success "$service updated successfully"
    done

    log_success "Rolling update completed"
}

# Start services
start_services() {
    local mode="${1:-detached}"

    log_info "Starting services in $mode mode..."

    if [ "$mode" == "detached" ]; then
        docker compose -f "$COMPOSE_FILE" up -d
    else
        docker compose -f "$COMPOSE_FILE" up
    fi

    log_success "Services started"
}

# Stop services
stop_services() {
    log_info "Stopping services..."

    docker compose -f "$COMPOSE_FILE" down

    log_success "Services stopped"
}

# View logs
view_logs() {
    local service="${1:-}"
    local lines="${2:-100}"

    if [ -n "$service" ]; then
        docker compose -f "$COMPOSE_FILE" logs --tail="$lines" "$service"
    else
        docker compose -f "$COMPOSE_FILE" logs --tail="$lines"
    fi
}

# Status check
status_check() {
    log_info "Checking service status..."

    docker compose -f "$COMPOSE_FILE" ps

    echo ""
    log_info "Backend health:"
    curl -sf http://localhost:8065/health || log_error "Backend not responding"
}

# Cleanup
cleanup() {
    log_info "Cleaning up unused resources..."

    docker compose -f "$COMPOSE_FILE" down --volumes --remove-orphans
    docker system prune -af --volumes

    log_success "Cleanup completed"
}

# Show help
show_help() {
    echo "InfraMon Deployment Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start [detached|foreground]  Start services"
    echo "  stop                        Stop all services"
    echo "  restart                     Restart services"
    echo "  build                       Build images from scratch"
    echo "  deploy                      Deploy with rolling update"
    echo "  logs [service] [lines]      View logs"
    echo "  status                      Show service status"
    echo "  health                      Check service health"
    echo "  migrate                     Run database migrations"
    echo "  cleanup                     Remove all containers, volumes, and images"
    echo "  help                        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  COMPOSE_FILE       Docker Compose file to use (default: docker-compose.yml)"
    echo "  COMPOSE_OVERRIDE   Override file to use"
    echo "  ENV_FILE           Environment file (default: .env)"
    echo ""
    echo "Examples:"
    echo "  $0 start detached    Start services in background"
    echo "  $0 deploy            Rolling update production"
    echo "  $0 logs backend 50   View last 50 backend logs"
}

# Main entry point
main() {
    local command="${1:-help}"
    shift || true

    # Export compose file path
    export COMPOSE_FILE

    case "$command" in
        start)
            local mode="${1:-detached}"
            check_prerequisites
            start_services "$mode"
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            start_services detached
            ;;
        build)
            check_prerequisites
            build_images
            ;;
        deploy)
            check_prerequisites
            rolling_update
            ;;
        logs)
            view_logs "$@"
            ;;
        status)
            status_check
            ;;
        health)
            health_check 30
            ;;
        migrate)
            run_migrations
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
