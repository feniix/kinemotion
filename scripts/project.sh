#!/bin/bash
# Main project management wrapper script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_SCRIPTS_DIR="$SCRIPT_DIR/project"

if [ $# -lt 1 ]; then
    echo "Kinemotion GitHub Project Management"
    echo "====================================="
    echo ""
    echo "Usage: $(basename $0) <command> [options]"
    echo ""
    echo "Commands:"
    echo "  add <title> <body> [options]      Create and add issue to project"
    echo "  set-field <issue> <field> <value> Set a custom field value"
    echo "  set-status <issue> <status>       Update issue status"
    echo "  batch-set <issue> [--field value]  Set multiple fields at once"
    echo "  list [--filter value]              List project items with filtering"
    echo "  summary                            Show project overview and stats"
    echo ""
    echo "Examples:"
    echo "  $(basename $0) add 'New feature' 'Description' --priority High --complexity 3"
    echo "  $(basename $0) set-field 5 Priority High"
    echo "  $(basename $0) set-status 5 'In Progress'"
    echo "  $(basename $0) batch-set 5 --priority High --effort 8 --status 'In Progress'"
    echo "  $(basename $0) list --domain Testing --priority High"
    echo "  $(basename $0) summary"
    echo ""
    echo "For more details, see: $PROJECT_SCRIPTS_DIR/README.md"
    exit 0
fi

COMMAND="$1"
shift

case "$COMMAND" in
    add)
        "$PROJECT_SCRIPTS_DIR/add-issue.sh" "$@"
        ;;
    set-field)
        "$PROJECT_SCRIPTS_DIR/set-field.sh" "$@"
        ;;
    set-status)
        "$PROJECT_SCRIPTS_DIR/set-status.sh" "$@"
        ;;
    batch-set)
        "$PROJECT_SCRIPTS_DIR/batch-set-fields.sh" "$@"
        ;;
    list)
        "$PROJECT_SCRIPTS_DIR/list.sh" "$@"
        ;;
    summary)
        "$PROJECT_SCRIPTS_DIR/summary.sh" "$@"
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo "Run '$(basename $0)' for help"
        exit 1
        ;;
esac
