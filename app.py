"""
Flask Application - Production Ready
"""
import os
import logging
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Static information as metric
metrics.info("app_info", "Application info", version="1.0.0")

APP_ENV = os.environ.get("APP_ENV", "production")
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
SECRET_KEY = os.environ.get("SECRET_KEY", "changeme")


@app.route("/", methods=["GET"])
def index():
    logger.info("Root endpoint called")
    return jsonify({
        "message": "Flask CI/CD Demo Application - UPDATED!",
        "version": APP_VERSION,
        "environment": APP_ENV,
        "status": "running",
        "update": "Added new item to test CI/CD"
    }), 200


@app.route("/health", methods=["GET"])
def health():
    """Kubernetes liveness probe endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/ready", methods=["GET"])
def ready():
    """Kubernetes readiness probe endpoint."""
    return jsonify({"status": "ready"}), 200


@app.route("/api/v1/items", methods=["GET"])
def get_items():
    """Sample API endpoint."""
    items = [
        {"id": 1, "name": "Item One", "category": "demo"},
        {"id": 2, "name": "Item Two", "category": "demo"},
        {"id": 3, "name": "Item Three", "category": "demo"},
        {"id": 4, "name": "Item Four - NEW!", "category": "demo"},
        {"id": 5, "name": "Item Five - NEWEST!", "category": "demo"},
    ]
    logger.info("Items endpoint called, returning %d items", len(items))
    return jsonify({"items": items, "count": len(items)}), 200


@app.route("/api/v1/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Get a single item by ID."""
    if item_id < 1 or item_id > 5:
        logger.warning("Item %d not found", item_id)
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"id": item_id, "name": f"Item {item_id}", "category": "demo"}), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error("Internal server error: %s", error)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = APP_ENV == "development"
    logger.info("Starting Flask app on port %d (env=%s)", port, APP_ENV)
    app.run(host="0.0.0.0", port=port, debug=debug)
