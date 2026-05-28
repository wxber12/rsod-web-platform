FROM node:20-alpine AS build

WORKDIR /app

# npm mirror (China)
RUN npm config set registry https://registry.npmmirror.com

# API base URL for production (Nginx proxy)
ENV VITE_API_BASE_URL=/api

COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
