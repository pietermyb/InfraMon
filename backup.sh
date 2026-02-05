#!/bin/bash

# InfraMon Backup and Restore Script
# Backs up database and configuration files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
DATE=$(date +%Y%m%d_%H%M%S)

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Colors functions
info() { echo -e "[INFO] $1"; }
error() { echo -e "[ERROR] $1" >&2; }

backup_database() {
    local db_path="$1"
    local backup_file="${BACKUP_DIR}/inframon_db_${DATE}.sqlite3.gz"

    if [ -f "$db_path" ]; then
        mkdir -p "$BACKUP_DIR"
        gzip -c "$db_path" > "$backup_file"
        info "Database backed up to: $backup_file"
        echo "$backup_file"
    else
        error "Database file not found: $db_path"
        return 1
    fi
}

backup_config() {
    local config_file="$1"
    local backup_file="${BACKUP_DIR}/inframon_config_${DATE}.tar.gz"

    if [ -f "$config_file" ]; then
        mkdir -p "$BACKUP_DIR"
        tar -czf "$backup_file" -C "$(dirname "$config_file")" "$(basename "$config_file")"
        info "Configuration backed up to: $backup_file"
        echo "$backup_file"
    else
        error "Config file not found: $config_file"
        return 1
    fi
}

restore_database() {
    local backup_file="$1"
    local restore_path="$2"

    if [ -f "$backup_file" ]; then
        mkdir -p "$(dirname "$restore_path")"
        gunzip -c "$backup_file" > "$restore_path"
        info "Database restored to: $restore_path"
    else
        error "Backup file not found: $backup_file"
        return 1
    fi
}

list_backups() {
    if [ -d "$BACKUP_DIR" ]; then
        echo "Available backups in ${BACKUP_DIR}:"
        ls -lh "$BACKUP_DIR" | tail -n +4
    else
        info "No backups found in ${BACKUP_DIR}"
    fi
}

cleanup_old_backups() {
    local days="${1:-30}"

    if [ -d "$BACKUP_DIR" ]; then
        info "Removing backups older than ${days} days..."
        find "$BACKUP_DIR" -type f -name "*.sqlite3.gz" -mtime +"$days" -delete
        find "$BACKUP_DIR" -type f -name "*.tar.gz" -mtime +"$days" -delete
        info "Cleanup complete"
    fi
}

show_help() {
    echo "InfraMon Backup and Restore Script"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  db <path>           Backup database (default: ./backend/inframon.db)"
    echo "  config <path>       Backup .env file"
    echo "  restore <backup>    Restore database from backup"
    echo "  list                List available backups"
    echo "  cleanup [days]      Remove backups older than N days (default: 30)"
    echo ""
    echo "Environment Variables:"
    echo "  BACKUP_DIR          Directory for backups (default: ./backups)"
    echo ""
    echo "Examples:"
    echo "  $0 db ./backend/inframon.db"
    echo "  $0 config .env"
    echo "  $0 restore ./backups/inframon_db_20240205.sqlite3.gz"
    echo "  $0 list"
    echo "  $0 cleanup 7"
}

main() {
    local command="${1:-help}"
    shift || true

    export BACKUP_DIR

    case "$command" in
        db)
            backup_database "${1:-./backend/inframon.db}"
            ;;
        config)
            backup_config "${1:-.env}"
            ;;
        restore)
            restore_database "$1" "${2:-./backend/inframon.db}"
            ;;
        list)
            list_backups
            ;;
        cleanup)
            cleanup_old_backups "${1:-30}"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
