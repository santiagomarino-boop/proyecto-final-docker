"""Aplicacion Flask instrumentada para Prometheus (una instancia por contenedor)."""
import os
import time
from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
SERVER_NAME = os.getenv("SERVER_NAME", "server sin nombre")

# La etiqueta backend diferencia cada instancia en Prometheus/Grafana.
metrics = PrometheusMetrics(
    app,
    group_by="endpoint",
    default_labels={"backend": SERVER_NAME},
    excluded_paths=[r"^/health$", r"^/metrics$"],
)
metrics.info("app_info", "Informacion de la instancia Flask", backend=SERVER_NAME)

@app.get("/")
def index():
    answer = jsonify(
        mensaje="Proyecto final: proxy inverso y monitoreo",
        backend=SERVER_NAME,
        ruta=request.path,
    )
    answer.headers["X-Backend"] = SERVER_NAME
    return answer

@app.get("/health")
def health():
    return jsonify(status="ok", backend=SERVER_NAME)

@app.get("/slow")
def slow():
    # Simula una respuesta lenta para que las graficas muestren latencia.
    try:
        ms = int(request.args.get("ms", "350"))
    except ValueError:
        ms = 350
    ms = max(0, min(ms, 2000))
    time.sleep(ms / 1000)
    response = jsonify(backend=SERVER_NAME, demora_ms=ms)
    response.headers["X-Backend"] = SERVER_NAME
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
