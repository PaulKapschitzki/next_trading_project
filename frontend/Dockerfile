FROM node:18-alpine

WORKDIR /app

# System-Abhängigkeiten installieren
RUN apk add --no-cache libc6-compat

# Kopiere Package-Dateien für besseres Caching
COPY package.json package-lock.json* ./

# Installiere Abhängigkeiten
RUN npm ci

# Kopiere den Rest der Anwendung
COPY . .

# Bei Produktions-Build:
# RUN npm run build

# Starte die Anwendung im Dev-Modus
CMD ["npm", "run", "dev"]
