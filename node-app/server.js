const express = require('express');
const winston = require('winston');
const { ElasticsearchTransport } = require('winston-elasticsearch');
const promClient = require('prom-client');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3001;

// Prometheus metrics
const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

const httpRequestCounter = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status']
});

const errorCounter = new promClient.Counter({
  name: 'errors_total',
  help: 'Total errors',
  labelNames: ['type']
});

// Winston Logger with Elasticsearch transport
const esTransport = new ElasticsearchTransport({
  level: 'info',
  clientOpts: { node: 'http://elasticsearch:9200' },
  indexPrefix: 'logs'
});

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/app.log' }),
    esTransport,
    new winston.transports.Console()
  ]
});

// Middleware
app.use(express.json());
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    httpRequestCounter.inc({
      method: req.method,
      route: req.route?.path || req.path,
      status: res.statusCode
    });
    
    logger.info('HTTP Request', {
      method: req.method,
      url: req.url,
      status: res.statusCode,
      duration: duration,
      userAgent: req.get('user-agent'),
      ip: req.ip
    });
  });
  next();
});

// Routes
app.get('/', (req, res) => {
  logger.info('Home page accessed');
  res.json({ message: 'Node.js Logging Service', status: 'running' });
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.get('/api/users', (req, res) => {
  logger.info('Fetching users');
  res.json({ users: ['Alice', 'Bob', 'Charlie'] });
});

app.get('/api/error', (req, res) => {
  errorCounter.inc({ type: 'simulated_error' });
  logger.error('Simulated error endpoint accessed', { 
    error: 'This is a simulated error',
    stack: new Error().stack
  });
  res.status(500).json({ error: 'Simulated server error' });
});

app.get('/api/slow', async (req, res) => {
  logger.warn('Slow endpoint accessed');
  await new Promise(resolve => setTimeout(resolve, 3000));
  res.json({ message: 'Slow response completed' });
});

// Error handling middleware
app.use((err, req, res, next) => {
  errorCounter.inc({ type: 'server_error' });
  logger.error('Unhandled error', {
    error: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method
  });
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
  console.log(`Node.js app running on http://localhost:${PORT}`);
});

// Simulate periodic errors for testing
setInterval(() => {
  if (Math.random() < 0.1) {
    logger.error('Random simulated error occurred', {
      service: 'node-app',
      timestamp: new Date().toISOString()
    });
    errorCounter.inc({ type: 'random_error' });
  }
  
  if (Math.random() < 0.3) {
    logger.warn('High memory usage warning', {
      service: 'node-app',
      memoryUsage: process.memoryUsage()
    });
  }
}, 30000);