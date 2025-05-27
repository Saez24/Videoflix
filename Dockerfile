FROM node:24-alpine AS builder
WORKDIR /app

# Abhängigkeiten installieren
COPY package.json package-lock.json ./
RUN npm ci

# Anwendung kopieren und bauen
COPY . .
RUN npm run build --configuration=production

# Runtime-Stage mit Nginx
FROM nginx:latest

# Standard nginx index.html entfernen
RUN rm -rf /usr/share/nginx/html/*

# Nginx-Konfiguration kopieren
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Build-Ergebnisse kopieren - Inhalt des videoflix-Ordners
COPY --from=builder /app/dist/videoflix/browser /usr/share/nginx/html/

# Port freigeben
EXPOSE 80

# Nginx starten
CMD ["nginx", "-g", "daemon off;"]