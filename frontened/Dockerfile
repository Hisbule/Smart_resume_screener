# ---- Base Stage ----
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json ./
# Install dependencies including dev dependencies needed for build
RUN npm install

# ---- Build Stage ----
FROM base AS build
WORKDIR /app
COPY . .
# Set the backend API URL during build time (can be overridden at runtime)
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}
RUN echo "Using VITE_API_URL=${VITE_API_URL}"
# Build the React app
RUN npm run build

# ---- Production Stage ----
FROM nginx:stable-alpine AS production
# Copy built assets from the build stage
COPY --from=build /app/dist /usr/share/nginx/html
# Copy nginx config (optional, if you need custom config)
# COPY nginx.conf /etc/nginx/conf.d/default.conf
# Expose port 80
EXPOSE 80
# Start nginx
CMD ["nginx", "-g", "daemon off;"]