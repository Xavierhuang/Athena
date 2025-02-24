const fs = require('fs');
const path = require('path');

// Define paths
const logsDir = path.join(__dirname, '../logs');
const logFile = path.join(logsDir, 'app.log');

// Create logs directory if it doesn't exist
if (!fs.existsSync(logsDir)) {
  console.log('Creating logs directory...');
  fs.mkdirSync(logsDir);
}

// Create app.log if it doesn't exist
if (!fs.existsSync(logFile)) {
  console.log('Creating app.log file...');
  fs.writeFileSync(logFile, '=== Application Logs ===\n');
}

console.log('Log initialization complete!'); 