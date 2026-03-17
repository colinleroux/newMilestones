FROM node:20-alpine AS frontend
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY vite.config.js postcss.config.js tailwind.config.js ./
COPY src ./src
COPY deeds/templates ./deeds/templates
RUN npm run build

FROM python:3.12-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY deeds ./deeds
COPY migrations ./migrations
COPY instance ./instance
COPY run.py wsgi_app.py ./
COPY --from=frontend /app/deeds/static/vite /app/deeds/static/vite

EXPOSE 8000

FROM nginx:1.27-alpine AS nginx
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=backend /app/deeds/static /var/www/app/static
