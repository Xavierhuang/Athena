require('dotenv').config();
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const path = require('path');
const fs = require('fs');
const chatRoutes = require('./routes/chat');
const logger = require('./utils/logger');

const app = express();

logger.info('Server starting up...');

console.log('Starting server...');

// Create a write stream for logs
const accessLogStream = fs.createWriteStream(
  path.join(__dirname, 'logs', 'access.log'), 
  { flags: 'a' }
);

// Use morgan middleware with Apache combined format
app.use(morgan('combined', { stream: accessLogStream }));

// Middleware
app.use(cors());
app.use(express.json());

// Request logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  console.log('Request headers:', req.headers);
  console.log('Request body:', req.body);
  next();
});

// Test route
app.get('/test', (req, res) => {
  res.json({ message: 'Server is running!' });
});

// Routes
app.use('/api/chat', chatRoutes);

// Error logging middleware (place this after your routes)
app.use((err, req, res, next) => {
  console.error('=== Server Error ===');
  console.error('Time:', new Date().toISOString());
  console.error('URL:', req.url);
  console.error('Method:', req.method);
  console.error('Error:', err);
  console.error('Stack:', err.stack);
  res.status(500).json({ error: err.message });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  logger.info(`Server running on port ${PORT}`);
}); 