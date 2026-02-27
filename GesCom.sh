#!/usr/bin/env bash
set -euo pipefail

# --- Couleurs ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

AUTO_TIMEOUT=30

# --- Fonctions utilitaires ---
info()    { echo -e "${BLUE}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()   { echo -e "${RED}[ERR]${NC}   $1"; }

banner() {
    clear
    echo -e "${CYAN}${BOLD}"
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║     GesCom - Gestion Commerciale     ║"
    echo "  ║            NKF  v1.0.0               ║"
    echo "  ╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

# --- Menu interactif ---
show_menu() {
    echo -e "  ${BOLD}Que souhaitez-vous faire ?${NC}"
    echo ""
    echo -e "    ${GREEN}${BOLD}1${NC}  ${BOLD}Lancer l'application${NC}            ${DIM}(docker compose up)${NC}"
    echo -e "    ${BOLD}2${NC}  Arrêter tous les services          ${DIM}(docker compose down)${NC}"
    echo -e "    ${BOLD}3${NC}  Redémarrer l'application            ${DIM}(down + up)${NC}"
    echo -e "    ${BOLD}4${NC}  Afficher l'état des services        ${DIM}(docker compose ps)${NC}"
    echo -e "    ${BOLD}5${NC}  Afficher les logs                   ${DIM}(Ctrl+C pour quitter)${NC}"
    echo -e "    ${BOLD}6${NC}  Charger les données de démo         ${DIM}(seed_data.py)${NC}"
    echo -e "    ${BOLD}7${NC}  Lancer les migrations               ${DIM}(alembic upgrade)${NC}"
    echo -e "    ${BOLD}8${NC}  Lancer les tests                    ${DIM}(pytest)${NC}"
    echo -e "    ${BOLD}9${NC}  Reconstruire les images Docker      ${DIM}(docker build)${NC}"
    echo ""
    echo -e "    ${RED}${BOLD}A${NC}  ${RED}Tout supprimer et repartir de zéro${NC} ${DIM}(down -v)${NC}"
    echo ""
    echo -e "    ${BOLD}Q${NC}  Quitter"
    echo ""
}

prompt_with_countdown() {
    local remaining=$AUTO_TIMEOUT
    local choice=""

    while [[ $remaining -gt 0 ]]; do
        printf "\r  ${BOLD}Votre choix [1-9, A, Q]${NC} ${DIM}(lancement auto dans %2ds)${NC} : ${BOLD}" "$remaining"

        if read -r -t 1 -n 1 choice 2>/dev/null; then
            echo -e "${NC}"
            # Entrée vide = choix par défaut (1)
            if [[ -z "$choice" ]]; then
                MENU_CHOICE="1"
            else
                MENU_CHOICE="$choice"
            fi
            return
        fi

        remaining=$((remaining - 1))
    done

    # Timeout atteint
    echo -e "${NC}"
    echo ""
    info "Délai expiré, lancement automatique..."
    MENU_CHOICE="1"
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
    warn "Vérifiez les logs : option 5 du menu."
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

pause_and_return() {
    echo ""
    echo -e "  ${DIM}Appuyez sur Entrée pour revenir au menu...${NC}"
    read -r
}

# --- Commandes ---
cmd_start() {
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
        echo -e "  ${YELLOW}Tip :${NC} Utilisez l'option ${BOLD}6${NC} pour charger les données de démo."

        open_browser "http://localhost:8000/docs"
    fi
}

cmd_stop() {
    info "Arrêt des services..."
    docker compose down
    success "Application arrêtée."
}

cmd_restart() {
    info "Redémarrage des services..."
    docker compose down
    docker compose up -d --build
    wait_for_api
    success "Application redémarrée."
}

cmd_status() {
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
    echo -e "  ${DIM}Ctrl+C pour revenir au menu${NC}"
    echo ""
    docker compose logs -f --tail=100 || true
}

cmd_seed() {
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
    info "Exécution des migrations..."
    docker compose exec app alembic upgrade head
    success "Migrations appliquées."
}

cmd_test() {
    info "Lancement des tests..."
    docker compose exec app pip install -q aiosqlite 2>/dev/null
    docker compose exec app pytest --tb=short
}

cmd_build() {
    info "Reconstruction des images Docker..."
    docker compose build --no-cache
    success "Images reconstruites."
}

cmd_reset() {
    warn "Cette action va supprimer tous les conteneurs, volumes et données."
    echo -n -e "  ${BOLD}Tapez 'oui' pour confirmer :${NC} "
    read -r confirm
    if [[ "$confirm" == "oui" ]]; then
        info "Suppression complète..."
        docker compose down -v --remove-orphans
        success "Tout a été supprimé. Relancez avec l'option 1."
    else
        info "Annulé."
    fi
}

# --- Boucle principale du menu ---
run_menu() {
    while true; do
        banner
        show_menu
        prompt_with_countdown

        echo ""

        case "${MENU_CHOICE}" in
            1)       cmd_start   ; pause_and_return ;;
            2)       cmd_stop    ; pause_and_return ;;
            3)       cmd_restart ; pause_and_return ;;
            4)       cmd_status  ; pause_and_return ;;
            5)       cmd_logs    ;;
            6)       cmd_seed    ; pause_and_return ;;
            7)       cmd_migrate ; pause_and_return ;;
            8)       cmd_test    ; pause_and_return ;;
            9)       cmd_build   ; pause_and_return ;;
            [aA])    cmd_reset   ; pause_and_return ;;
            [qQ])
                echo -e "  ${CYAN}Au revoir !${NC}"
                echo ""
                exit 0
                ;;
            *)
                warn "Choix invalide : ${MENU_CHOICE}"
                sleep 1
                ;;
        esac
    done
}

# --- Point d'entrée ---
# Si un argument est passé en ligne de commande, exécution directe (non interactif)
if [[ $# -gt 0 ]]; then
    banner
    case "$1" in
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
        help|-h|--help)
            echo -e "${BOLD}Usage :${NC} $0 [commande]"
            echo ""
            echo "  Sans argument : lance le menu interactif"
            echo ""
            echo -e "${BOLD}Commandes directes :${NC}"
            echo "  start   stop   restart   status   logs"
            echo "  seed    migrate   test    build    reset"
            ;;
        *)
            error "Commande inconnue : $1"
            exit 1
            ;;
    esac
else
    # Mode interactif : afficher le menu
    run_menu
fi
