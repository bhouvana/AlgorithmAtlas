FROM node:20-slim AS builder

WORKDIR /app

# Install deps (cached layer)
COPY apps/frontend/package*.json ./apps/frontend/
RUN cd apps/frontend && npm ci

# Build
COPY apps/frontend ./apps/frontend
COPY packages ./packages
WORKDIR /app/apps/frontend
ARG VITE_API_URL=http://backend:8000
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# ── Production image ──────────────────────────────────────────────────────────
FROM nginx:1.27-alpine

# Apply security patches
RUN apk upgrade --no-cache

COPY --from=builder /app/apps/frontend/dist /usr/share/nginx/html

# SPA routing — all paths fall back to index.html
RUN printf 'server {\n\
  listen 80;\n\
  root /usr/share/nginx/html;\n\
  index index.html;\n\
  location / {\n\
    try_files $uri $uri/ /index.html;\n\
  }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
