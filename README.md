# Proyecto final — Docker, Nginx, Prometheus y Grafana

Proyecto de infraestructura containerizada con **3 instancias Flask**, proxy reverso Nginx,
Prometheus, Nginx Prometheus Exporter, cAdvisor y Grafana. Se incluye una red Docker
personalizada, volúmenes persistentes y pruebas de carga desde el equipo host con k6.

## Requisitos previos

- Docker Desktop con motor Docker activo; en Ubuntu/WSL2 habilitar **Settings → Resources → WSL Integration**.
- Docker Compose v2 (`docker compose version`).
- Al menos 4 GB de memoria asignada a Docker Desktop.
- Para pruebas desde la máquina anfitriona: [k6](https://grafana.com/docs/k6/latest/set-up/install-k6/).
- Puertos locales libres: **8082, 8083, 9091, 3001**.

## 1. Iniciar (en Ubuntu/WSL2)

```bash
cd ~/proyecto_final_docker
cp .env.example .env
# Opcional: abre .env y cambia la contraseña local de Grafana.
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

**No modifica el directorio `~/lab-proxy` del laboratorio anterior.**

## 2. URLs de acceso

| Servicio | Dirección en Chrome | Qué comprobar |
|---|---|---|
| Nginx balanceador | http://localhost:8082 | Respuesta JSON, campo `backend` |
| cAdvisor | http://localhost:8083 | Contenedores y métricas cuando el entorno lo permita |
| Prometheus | http://localhost:9091 | Status → Target health: **6 targets UP** |
| Grafana | http://localhost:3001 | Usuario `admin`, contraseña de `.env` |

Los seis targets corresponden a **app1, app2, app3, nginx-exporter, cadvisor y prometheus**.
El dashboard **Proyecto final - Monitoreo** se carga automáticamente desde la carpeta `grafana/dashboards/`.

## 3. Comprobar el balanceo

```bash
for i in $(seq 1 12); do curl -s http://localhost:8082/; echo; done
```

Verifica que las respuestas contengan `server 1`, `server 2` y `server 3`.
Si quieres comprobar las cabeceras: `curl -i http://localhost:8082/`.

## 4. Comprobar métricas

```bash
curl -s http://localhost:8082/health
curl -s http://localhost:8083/metrics | head -n 5
```

En Prometheus (`http://localhost:9091`), ejecuta en Query:

```promql
up
sum by (backend) (rate(flask_http_request_total[1m]))
histogram_quantile(0.95, sum by (le, backend) (rate(flask_http_request_duration_seconds_bucket[1m])))
nginx_connections_active
sum by (name) (rate(container_cpu_usage_seconds_total{name!=""}[1m]))
```

**Nota:** en Docker Desktop + WSL2, cAdvisor puede presentar métricas sin las etiquetas
`name` o `id`, aunque el target aparezca en UP. Si el panel de CPU está vacío,
usa `docker stats --no-stream` como respaldo y explica la limitación en el informe.

## 5. Ejecutar carga desde la máquina física

Instala k6 en **Windows** y, desde PowerShell, entra a la carpeta del proyecto (o a `pruebas`):

```powershell
k6 run .\pruebas\carga.js
```

Como el script envía peticiones a `http://localhost:8082`, también puede ejecutarse desde
WSL si tienes k6 allí instalado: `k6 run pruebas/carga.js`.

Durante la prueba, abre Grafana → **Dashboards → Proyecto final → Proyecto final - Monitoreo**,
selecciona **Last 15 minutes** y **Refresh 5s**. Guarda capturas de las gráficas y del resumen de k6.

## 6. Probar caída de una instancia

Terminal B (k6 desde el host):

```powershell
k6 run .\pruebas\falla.js
```

Terminal principal (Ubuntu/WSL2), mientras el test está activo:

```bash
docker compose stop app1
```

En Prometheus consulta `up{job="backends"}`. Tras el siguiente sondeo (5 s), `app1` debería
marcar **0**, mientras `app2` y `app3` continúan en **1**. En Grafana, las series de `server 2`
y `server 3` deben seguir atendiendo solicitudes. Toma evidencia antes de recuperar la instancia.

Para recuperarla:

```bash
docker compose start app1
docker compose ps
```

No inventes un tiempo de recuperación: mídelo o aclara que no pudo medirse.

## 7. Evidencias para el informe

1. `docker compose ps` con los **8 servicios** activos (no incluye k6 instalado en el host).
2. `curl` alternando entre **tres** backends.
3. Prometheus **Target health 6/6 UP**.
4. Grafana con gráficas durante k6.
5. Resumen final real de k6 (HTTP, latencia p95, throughput, errores).
6. Prueba de falla de `app1`, Prometheus `up` y recuperación.
7. `docker stats` cuando cAdvisor no muestre datos individuales.

Copia los resultados y las capturas reales al archivo `informe/Informe_Proyecto_Final.docx`.

## 8. Publicar el repositorio

```bash
git init
git add .
git commit -m "Proyecto final de monitoreo con Docker"
# Crea un repositorio vacío en GitHub y copia su URL:
git branch -M main
git remote add origin URL_DE_TU_REPOSITORIO
git push -u origin main
```

**No subas `.env` al repositorio:** está incluido en `.gitignore`.

## 9. Apagar sin perder el trabajo

```bash
docker compose down
```

Los datos de Prometheus y Grafana permanecen en volúmenes con nombre.
No ejecutes `docker compose down -v` salvo que quieras **eliminar los datos**.

## Entrega final

En la plataforma, cada integrante entrega individualmente:
**PDF del informe con todos los nombres**, URL del **repositorio GitHub** y URL del
**video de presentación (máximo 10 minutos)**. Cada integrante debe aparecer al menos **un minuto**.
