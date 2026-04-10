const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const io = require('socket.io')(3001);

const app = express();

// API Routes
app.get('/api/robots', (req, res) => {
  res.json([
    { id: 'pirc-01', status: 'online', battery: 87, position: [1.2, 0.8] },
    { id: 'pirc-02', status: 'online', battery: 92, position: [-1.5, 2.1] }
  ]);
});

app.get('/api/stats', (req, res) => {
  res.json({
    fps: 58.3,
    latency: 22,
    cpu: 34,
    memory: 2.1
  });
});

// RTSP Proxy (WebRTC)
app.use('/stream', createProxyMiddleware({
  target: 'rtsp://localhost:8554/',
  changeOrigin: true,
  ws: true
}));

// Socket.IO for real-time telemetry
io.on('connection', (socket) => {
  console.log('Dashboard connected');
  
  // Broadcast robot telemetry
  const telemetryInterval = setInterval(() => {
    socket.emit('telemetry', {
      robots: [
        { id: 'pirc-01', pose: [Math.random()*2-1, Math.random()*2-1, 0] },
        { id: 'pirc-02', pose: [Math.random()*2-1, Math.random()*2-1, 0] }
      ]
    });
  }, 100);
  
  socket.on('disconnect', () => {
    clearInterval(telemetryInterval);
  });
});

app.listen(8080, () => {
  console.log('🚀 PiRC Dashboard API on http://localhost:8080');
});
