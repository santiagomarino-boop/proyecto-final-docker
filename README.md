# Proyecto final - Proxy inverso y monitoreo con Docker

## Descripción del proyecto

En este proyecto configuramos una infraestructura con Docker Compose para ejecutar tres servidores Flask y distribuir las peticiones entre ellos mediante Nginx.

También usamos Prometheus y Grafana para revisar las solicitudes, los tiempos de respuesta y el uso de recursos. Para comprobar el comportamiento de los servidores realizamos pruebas de carga con k6 y una prueba de falla deteniendo temporalmente una instancia.

## Herramientas utilizadas

- Docker y Docker Compose
- Python y Flask
- Nginx
- Prometheus
- Nginx Prometheus Exporter
- cAdvisor
- Grafana
- Telegraf
- k6 (para las pruebas)

## Archivos del proyecto

- `backend/`: aplicación Flask, dependencias y Dockerfile.
- `nginx/`: configuración de Nginx como proxy inverso y balanceador.
- `prometheus/`: configuración de los servicios que se monitorean.
- `grafana/`: configuración de Grafana y archivo JSON del dashboard.
- `monitoring/telegraf/`: configuración de Telegraf para obtener métricas de contenedores.
- `pruebas/`: scripts `carga.js` y `falla.js` utilizados con k6.
- `docker-compose.yml`: definición de servicios, red y volúmenes.
- `.env.example`: ejemplo de variables de entorno.

## Requisitos previos

- Docker Desktop con Docker Compose v2, o Docker Engine con el complemento Compose.
- Si se utiliza Ubuntu en WSL2, tener habilitada la integración de Docker Desktop.
- Puertos locales disponibles: `8082`, `8083`, `9091` y `3001`.
- k6 instalado en el equipo desde el que se ejecutarán las pruebas.

## Iniciar el proyecto

Clonar el repositorio y entrar a la carpeta:

```bash
git clone https://github.com/santiagomarino-boop/proyecto-final-docker.git
cd proyecto-final-docker
```

Crear el archivo de variables de entorno y configurar la contraseña local de Grafana si es necesario:

```bash
cp .env.example .env
```

Comprobar la configuración e iniciar los contenedores:

```bash
docker compose config --quiet
docker compose up -d --build
docker compose ps
```

Docker Compose define nueve servicios: `app1`, `app2`, `app3`, `nginx`, `nginx-exporter`, `cadvisor`, `prometheus`, `grafana` y `telegraf`.

## Direcciones de acceso

| Servicio | Dirección |
|---|---|
| Aplicación por Nginx | http://localhost:8082 |
| cAdvisor | http://localhost:8083 |
| Prometheus | http://localhost:9091 |
| Grafana | http://localhost:3001 |

Para ingresar a Grafana se utiliza el usuario `admin` y la contraseña establecida en `.env`.

## Comprobar el balanceo de carga

Nginx distribuye las peticiones entre tres instancias Flask. Cada una indica en su respuesta cuál servidor atendió la solicitud.

```bash
for i in $(seq 1 12); do
    curl -s http://localhost:8082/
    echo
done
```

Al repetir las solicitudes deben aparecer respuestas de los servidores 1, 2 y 3. También se puede comprobar el estado de la aplicación con:

```bash
curl http://localhost:8082/health
```

## Monitoreo

Prometheus recopila las métricas de los tres servidores Flask, el exportador de Nginx, cAdvisor, Telegraf y el propio Prometheus.

En `http://localhost:9091` se puede consultar:

```promql
up
```

En nuestras pruebas verificamos siete targets en estado `UP`.

En Grafana se pueden revisar paneles de peticiones por segundo, latencia, consumo de CPU y memoria, conexiones de Nginx, errores HTTP, disponibilidad y actividad de red y disco.

Durante la configuración observamos que cAdvisor no mostraba todas las métricas individuales de los contenedores en Docker Desktop con WSL2. Para complementar esa información configuramos Telegraf y corregimos las consultas de los paneles.

## Pruebas de carga con k6

Desde el equipo que tenga k6 instalado, ubicarse en la carpeta del proyecto y ejecutar:

```bash
k6 run pruebas/carga.js
```

Durante la ejecución se pueden observar las gráficas de Grafana. En una de las pruebas realizadas obtuvimos 4.526 solicitudes, 100 % de comprobaciones exitosas, 0 % de fallos y una latencia p95 de 354,22 ms. Los resultados pueden variar en otra ejecución.

## Prueba de falla de un servidor

Para generar solicitudes durante la prueba utilizamos:

```bash
k6 run pruebas/falla.js
```

Mientras la prueba está activa, desde otra terminal detenemos `app1`:

```bash
docker compose stop app1
```

Comprobamos la disponibilidad con la consulta `up{job="backends"}` en Prometheus y verificamos que las otras instancias siguen atendiendo solicitudes. Después recuperamos el servidor:

```bash
docker compose start app1
docker compose ps
```

## Detener la infraestructura

```bash
docker compose down
```

Este comando detiene y retira los contenedores sin eliminar los volúmenes de datos de Prometheus y Grafana.
