# Supervision avec Grafana et Prometheus 📊

Une pile de supervision complète, lancée en une seule commande avec Docker Compose :

- **Application de démonstration** (Python) : simule le trafic d'une boutique en ligne et expose des métriques
- **Prometheus** : collecte les métriques toutes les 5 secondes
- **Grafana** : affiche un tableau de bord configuré automatiquement au démarrage

```
┌──────────────┐  /metrics   ┌──────────────┐   PromQL   ┌──────────────┐
│  Application │ ◄────────── │  Prometheus  │ ◄───────── │   Grafana    │
│    :8000     │             │    :9090     │            │    :3000     │
└──────────────┘             └──────────────┘            └──────────────┘
```

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows, macOS ou Linux)

## Démarrage

```bash
git clone https://github.com/VOTRE-UTILISATEUR/grafana-monitoring.git
cd grafana-monitoring
docker compose up -d --build
```

Ouvrez ensuite :

| Service     | Adresse                         | Identifiants      |
|-------------|---------------------------------|-------------------|
| Grafana     | http://localhost:3000           | `admin` / `admin` |
| Prometheus  | http://localhost:9090           | —                 |
| Métriques   | http://localhost:8000/metrics   | —                 |

Le tableau de bord **Boutique en ligne — Vue d'ensemble** s'affiche dès la page d'accueil de Grafana.
Attendez une à deux minutes pour que les graphiques se remplissent.

Pour arrêter :

```bash
docker compose down        # arrête les conteneurs
docker compose down -v     # arrête et supprime aussi les données
```

## Le tableau de bord

| Panneau                  | Requête PromQL                                                                 |
|--------------------------|--------------------------------------------------------------------------------|
| Requêtes par seconde     | `sum(rate(app_requests_total[1m]))`                                            |
| Taux d'erreur (5xx)      | `100 * sum(rate(app_requests_total{status=~"5.."}[1m])) / sum(rate(app_requests_total[1m]))` |
| Latence p95              | `histogram_quantile(0.95, sum by (le) (rate(app_request_duration_seconds_bucket[1m])))` |
| Trafic par page          | `sum by (endpoint) (rate(app_requests_total[1m]))`                             |
| Réponses par code HTTP   | `sum by (status) (rate(app_requests_total[1m]))`                               |
| Commandes par minute     | `60 * rate(app_orders_total[1m])`                                              |

La charge simulée suit un cycle de 10 minutes : la latence et le taux d'erreur montent avec le trafic.

## Métriques exposées

| Métrique                        | Type       | Description                        |
|---------------------------------|------------|------------------------------------|
| `app_requests_total`            | Compteur   | Requêtes par page, méthode et code |
| `app_request_duration_seconds`  | Histogramme| Durée des requêtes                 |
| `app_active_users`              | Jauge      | Utilisateurs actifs                |
| `app_orders_total`              | Compteur   | Commandes validées                 |
| `app_revenue_total`             | Compteur   | Chiffre d'affaires cumulé          |

## Structure

```
grafana-monitoring/
├── docker-compose.yml
├── app/
│   ├── app.py              # Application qui génère les métriques
│   ├── Dockerfile
│   └── requirements.txt
├── prometheus/
│   └── prometheus.yml      # Cibles à collecter
└── grafana/
    ├── dashboards/
    │   └── boutique.json   # Tableau de bord
    └── provisioning/       # Source de données et tableaux chargés au démarrage
```

## Changer le mot de passe Grafana

Créez un fichier `.env` à la racine (il est ignoré par Git) :

```
GRAFANA_USER=admin
GRAFANA_PASSWORD=un-mot-de-passe-solide
```

Le mot de passe n'est pris en compte qu'à la première création du volume. Si Grafana a déjà été lancé,
exécutez `docker compose down -v` avant de redémarrer.

## Idées d'amélioration

- Ajouter des alertes Grafana (par exemple : taux d'erreur supérieur à 3 %)
- Ajouter `node-exporter` pour superviser la machine (processeur, mémoire, disque)
- Remplacer l'application simulée par une vraie API (Flask, FastAPI, Express…)
- Ajouter Loki pour centraliser les journaux
