from app.models.article import Article, ArticleTaille, ArticleCouleur, ArticleDepot, ArticleTarif
from app.models.client import Client, ContactClient, AdresseClient
from app.models.commande import Commande, LigneCommande
from app.models.facture import Facture, LigneFacture
from app.models.stock import MouvementStock, LigneMouvementStock, Inventaire, LigneInventaire
from app.models.livraison import BonLivraison, LigneBonLivraison
from app.models.vrp import VRP, Concession, SuiviClient, Intervention
from app.models.user import User, Role
from app.models.fournisseur import Fournisseur, Revendeur
from app.models.transport import Transport

__all__ = [
    "Article", "ArticleTaille", "ArticleCouleur", "ArticleDepot", "ArticleTarif",
    "Client", "ContactClient", "AdresseClient",
    "Commande", "LigneCommande",
    "Facture", "LigneFacture",
    "MouvementStock", "LigneMouvementStock", "Inventaire", "LigneInventaire",
    "BonLivraison", "LigneBonLivraison",
    "VRP", "Concession", "SuiviClient", "Intervention",
    "User", "Role",
    "Fournisseur", "Revendeur",
    "Transport",
]
