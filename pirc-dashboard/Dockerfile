FROM node:20-alpine

# PiRC Dashboard - React + FastAPI + WebRTC
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# RTSP Proxy + API
EXPOSE 8080 8554 9090 3000

CMD ["sh", "-c", "node server/server.js & npm start"]
