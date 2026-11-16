"""Application de démonstration : simule le trafic d'une boutique en ligne
et expose des métriques Prometheus sur http://localhost:8000/metrics."""

import math
import random
import time

from prometheus_client import Counter, Gauge, Histogram, start_http_server

REQUESTS = Counter(
    "app_requests_total",
    "Nombre total de requêtes HTTP traitées",
    ["endpoint", "method", "status"],
)
DURATION = Histogram(
    "app_request_duration_seconds",
    "Durée des requêtes HTTP en secondes",
    ["endpoint"],
    buckets=(0.025, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.5, 5.0),
)
ACTIVE_USERS = Gauge("app_active_users", "Utilisateurs actifs en ce moment")
ORDERS = Counter("app_orders_total", "Nombre total de commandes validées")
REVENUE = Counter("app_revenue_total", "Chiffre d'affaires cumulé")

# endpoint: (méthode, poids dans le trafic, latence moyenne en s, taux d'erreur)
ENDPOINTS = {
    "/": ("GET", 40, 0.06, 0.002),
    "/produits": ("GET", 30, 0.12, 0.005),
    "/panier": ("POST", 15, 0.18, 0.010),
    "/paiement": ("POST", 8, 0.45, 0.040),
    "/connexion": ("POST", 7, 0.15, 0.020),
}
NAMES = list(ENDPOINTS)
WEIGHTS = [ENDPOINTS[name][1] for name in NAMES]


def simulate_request(load: float) -> None:
    endpoint = random.choices(NAMES, weights=WEIGHTS)[0]
    method, _, latency, error_rate = ENDPOINTS[endpoint]

    # Plus la charge est forte, plus les requêtes sont lentes et fragiles.
    duration = random.lognormvariate(math.log(latency * (0.7 + load)), 0.45)
    roll = random.random()
    if roll < error_rate * (0.5 + 1.5 * load):
        status = "500"
    elif roll < 0.04:
        status = "404" if method == "GET" else "400"
    else:
        status = "200"

    REQUESTS.labels(endpoint=endpoint, method=method, status=status).inc()
    DURATION.labels(endpoint=endpoint).observe(duration)

    if endpoint == "/paiement" and status == "200":
        ORDERS.inc()
        REVENUE.inc(round(random.uniform(8, 180), 2))


def main() -> None:
    start_http_server(8000)
    print("Métriques disponibles sur http://localhost:8000/metrics", flush=True)

    start = time.time()
    while True:
        elapsed = time.time() - start
        # La charge oscille entre 0 et 1 sur un cycle de 10 minutes,
        # pour que les graphiques aient du relief.
        load = 0.5 + 0.5 * math.sin(2 * math.pi * elapsed / 600)

        ACTIVE_USERS.set(round(40 + 160 * load + random.uniform(-8, 8)))
        for _ in range(random.randint(1, 3 + int(12 * load))):
            simulate_request(load)

        time.sleep(0.25)


if __name__ == "__main__":
    main()
