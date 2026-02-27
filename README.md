# GesCom - Gestion Commerciale NKF

Application de gestion commerciale migrée depuis WinDev vers Python/FastAPI.

## Stack Technique

- **Backend** : Python 3.12+ / FastAPI / SQLAlchemy 2.0
- **Base de données** : PostgreSQL 16
- **Cache** : Redis 7
- **Auth** : JWT + RBAC (6 rôles)
- **CI/CD** : GitHub Actions
- **Conteneurs** : Docker / Docker Compose

## Modules

| Module | Description |
|--------|-------------|
| Articles | Catalogue produits, variantes, tarifs |
| Clients | Gestion clientèle, contacts, adresses |
| Commandes | Processus de commande complet |
| Factures | Facturation et suivi paiements |
| Stock | Mouvements, inventaires, surveillance |
| Livraisons | BL, expédition, transport |
| VRP | Force de vente, concessions, commissions |
| Reporting | Statistiques, analyses, exports |

## Démarrage rapide

### Avec Docker (recommandé)

```bash
cp .env.example .env
docker compose up -d
```

L'API est accessible sur http://localhost:8000

Documentation Swagger : http://localhost:8000/docs

### En local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

### Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
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
│   ├── api/v1/          # Routes API REST
│   ├── auth/            # Authentification JWT
│   ├── models/          # Modèles SQLAlchemy
│   ├── schemas/         # Schémas Pydantic
│   ├── services/        # Logique métier
│   └── utils/           # Utilitaires
├── alembic/             # Migrations DB
├── tests/               # Tests automatisés
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```
