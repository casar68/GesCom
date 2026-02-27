#!/usr/bin/env bash
set -euo pipefail

# --- Couleurs ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# --- Fonctions utilitaires ---
info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERR]${NC}   $1"; }

banner() {
    echo -e "${CYAN}${BOLD}"
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║     GesCom - Gestion Commerciale     ║"
    echo "  ║          NKF  v1.0.0                 ║"
    echo "  ╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

usage() {
    echo -e "${BOLD}Usage :${NC} $0 [commande]"
    echo ""
    echo -e "${BOLD}Commandes :${NC}"
    echo "  start       Démarrer l'application (par défaut)"
    echo "  stop        Arrêter l'application"
    echo "  restart     Redémarrer l'application"
    echo "  status      Afficher l'état des services"
    echo "  logs        Afficher les logs (Ctrl+C pour quitter)"
    echo "  seed        Peupler la base avec les données de démo"
    echo "  migrate     Lancer les migrations Alembic"
    echo "  test        Lancer les tests"
    echo "  build       Reconstruire les images Docker"
    echo "  reset       Tout supprimer et repartir de zéro"
    echo "  help        Afficher cette aide"
    echo ""
    echo -e "${BOLD}Exemples :${NC}"
    echo "  ./GesCom.sh              # Démarrer"
    echo "  ./GesCom.sh stop         # Arrêter"
    echo "  ./GesCom.sh logs         # Voir les logs"
    echo "  ./GesCom.sh seed         # Charger les données démo"
}

# --- Vérifications préalables ---
check_prerequisites() {
    local missing=0

    if ! command -v docker &>/dev/null; then
        error "Docker n'est pas installé. https://docs.docker.com/get-docker/"
        missing=1
    fi

    if ! docker compose version &>/dev/null 2>&1; then
        error "Docker Compose n'est pas disponible."
        missing=1
    fi

    if ! docker info &>/dev/null 2>&1; then
        error "Le daemon Docker n'est pas démarré. Lancez Docker Desktop."
        missing=1
    fi

    if [[ $missing -eq 1 ]]; then
        exit 1
    fi

    success "Prérequis OK (Docker + Compose)"
}

# --- .env ---
ensure_env() {
    if [[ ! -f .env ]]; then
        warn "Fichier .env absent, création depuis .env.example..."
        cp .env.example .env
        success ".env créé"
    fi
}

# --- Attendre que l'API soit prête ---
wait_for_api() {
    local max_attempts=30
    local attempt=0
    info "Attente du démarrage de l'API..."

    while [[ $attempt -lt $max_attempts ]]; do
        if curl -sf http://localhost:8000/health &>/dev/null; then
            success "API prête sur http://localhost:8000"
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done

    warn "L'API n'a pas répondu après ${max_attempts} tentatives."
    warn "Vérifiez les logs : ./GesCom.sh logs"
    return 1
}

# --- Ouvrir le navigateur ---
open_browser() {
    local url="$1"
    if command -v open &>/dev/null; then
        open "$url"
    elif command -v xdg-open &>/dev/null; then
        xdg-open "$url"
    fi
}

# --- Commandes ---
cmd_start() {
    banner
    check_prerequisites
    ensure_env

    info "Démarrage des services..."
    docker compose up -d --build

    if wait_for_api; then
        echo ""
        echo -e "${GREEN}${BOLD}  Application démarrée avec succès !${NC}"
        echo ""
        echo -e "  ${BOLD}Frontend :${NC}  http://localhost"
        echo -e "  ${BOLD}API :${NC}       http://localhost:8000"
        echo -e "  ${BOLD}Swagger :${NC}   http://localhost:8000/docs"
        echo ""
        echo -e "  ${BOLD}Comptes démo :${NC}"
        echo -e "    Admin :      admin@gescom.fr / admin123"
        echo -e "    Commercial : demo@gescom.fr  / demo123"
        echo ""
        echo -e "  ${YELLOW}Tip :${NC} Lancez ${BOLD}./GesCom.sh seed${NC} pour charger les données de démo."
        echo ""

        open_browser "http://localhost:8000/docs"
    fi
}

cmd_stop() {
    banner
    info "Arrêt des services..."
    docker compose down
    success "Application arrêtée."
}

cmd_restart() {
    banner
    info "Redémarrage des services..."
    docker compose down
    docker compose up -d --build
    wait_for_api
    success "Application redémarrée."
}

cmd_status() {
    banner
    docker compose ps

    echo ""
    if curl -sf http://localhost:8000/health &>/dev/null; then
        local health
        health=$(curl -sf http://localhost:8000/health)
        success "API : $health"
    else
        warn "API non accessible"
    fi
}

cmd_logs() {
    docker compose logs -f --tail=100
}

cmd_seed() {
    banner
    info "Chargement des données de démonstration..."
    docker compose exec app python scripts/seed_data.py
    success "Données de démo chargées."
    echo ""
    echo -e "  ${BOLD}Comptes créés :${NC}"
    echo "    admin@gescom.fr / admin123   (admin)"
    echo "    demo@gescom.fr  / demo123    (commercial)"
    echo ""
    echo -e "  ${BOLD}Données :${NC} 12 articles, 8 clients, 3 VRP, 2 transporteurs"
}

cmd_migrate() {
    banner
    info "Exécution des migrations..."
    docker compose exec app alembic upgrade head
    success "Migrations appliquées."
}

cmd_test() {
    banner
    info "Lancement des tests..."
    docker compose exec app pip install -q aiosqlite 2>/dev/null
    docker compose exec app pytest --tb=short
}

cmd_build() {
    banner
    info "Reconstruction des images Docker..."
    docker compose build --no-cache
    success "Images reconstruites."
}

cmd_reset() {
    banner
    warn "Cette action va supprimer tous les conteneurs, volumes et données."
    echo -n -e "  ${BOLD}Confirmer ? (oui/non) :${NC} "
    read -r confirm
    if [[ "$confirm" == "oui" ]]; then
        info "Suppression complète..."
        docker compose down -v --remove-orphans
        success "Tout a été supprimé. Relancez avec ./GesCom.sh start"
    else
        info "Annulé."
    fi
}

# --- Point d'entrée ---
COMMAND="${1:-start}"

case "$COMMAND" in
    start)   cmd_start   ;;
    stop)    cmd_stop    ;;
    restart) cmd_restart ;;
    status)  cmd_status  ;;
    logs)    cmd_logs    ;;
    seed)    cmd_seed    ;;
    migrate) cmd_migrate ;;
    test)    cmd_test    ;;
    build)   cmd_build   ;;
    reset)   cmd_reset   ;;
    help|-h|--help) usage ;;
    *)
        error "Commande inconnue : $COMMAND"
        echo ""
        usage
        exit 1
        ;;
esac
