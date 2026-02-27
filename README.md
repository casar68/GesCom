# GesCom - Gestion Commerciale NKF

Application de gestion commerciale migrée depuis WinDev vers Python/FastAPI + React.

## Stack Technique

| Couche | Technologie |
|--------|------------|
| **Backend** | Python 3.12+ / FastAPI / SQLAlchemy 2.0 |
| **Frontend** | React 19 / Vite 6 / Tailwind CSS 3 |
| **Base de données** | PostgreSQL 16 |
| **Cache** | Redis 7 |
| **Auth** | JWT + RBAC (6 rôles) |
| **Reporting** | ReportLab (PDF) / OpenPyXL (Excel) / Recharts (graphiques) |
| **CI/CD** | GitHub Actions |
| **Conteneurs** | Docker / Docker Compose |

## Modules

| Module | Endpoints | Description |
|--------|-----------|-------------|
| Articles | 9 | Catalogue produits, variantes (taille/couleur), tarifs, dépôts |
| Clients | 7 | Gestion clientèle, contacts multiples, adresses |
| Commandes | 7 | Workflow complet : brouillon -> validée -> facturée/livrée |
| Factures | 4 | Facturation, paiements partiels/complets, export PDF |
| Livraisons | 5 | BL, expédition, workflow livraison, reliquats |
| Stock | 5 | Mouvements, inventaires, alertes seuil minimum |
| VRP | 5 | Force de vente, concessions, suivi client |
| Reporting | 9 | Dashboard, CA mensuel, top clients/articles, export Excel |

**Total : 51+ endpoints API REST**

## Démarrage rapide

### Avec Docker (recommandé)

```bash
cp .env.example .env
docker compose up -d
```

- Frontend : http://localhost
- API : http://localhost:8000
- Swagger : http://localhost:8000/docs

### En local (développement)

**Backend :**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

**Frontend :**
```bash
cd frontend
npm install
npm run dev
```

### Données de démonstration

```bash
python scripts/seed_data.py
```

Crée : 2 utilisateurs, 12 articles, 8 clients, 3 VRP, 2 transporteurs.

Comptes démo :
- Admin : `admin@gescom.fr` / `admin123`
- Commercial : `demo@gescom.fr` / `demo123`

### Migration des données HyperFile

```bash
# 1. Exporter les tables HyperFile en CSV depuis WinDev
# 2. Placer les CSV dans data/
python scripts/migrate_hyperfile.py
```

## Tests

```bash
pip install aiosqlite
pytest
```

## Structure du projet

```
GesCom/
├── app/
│   ├── api/v1/          # 8 modules de routes API REST
│   ├── auth/            # Authentification JWT + RBAC
│   ├── models/          # 11 modèles SQLAlchemy (22 tables)
│   ├── schemas/         # Schémas Pydantic (validation E/S)
│   ├── services/        # Logique métier (7 services)
│   └── utils/           # Utilitaires
├── frontend/
│   ├── src/
│   │   ├── components/  # Composants React (Layout, etc.)
│   │   ├── pages/       # 6 pages (Login, Dashboard, Articles, ...)
│   │   ├── context/     # Contexte Auth React
│   │   └── services/    # Client API Axios
│   └── Dockerfile       # Build prod Nginx
├── scripts/             # Seed data + migration HyperFile
├── alembic/             # Migrations DB
├── tests/               # 40+ tests automatisés
├── docker-compose.yml   # Stack complète (4 services)
├── Dockerfile           # Backend Python
└── pyproject.toml       # Dépendances Python
```
