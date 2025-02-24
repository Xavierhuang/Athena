const fs = require('fs');
const path = require('path');

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '../logs');
console.log('Logs directory path:', logsDir);  // Debug log

if (!fs.existsSync(logsDir)) {
  console.log('Creating logs directory...');  // Debug log
  fs.mkdirSync(logsDir);
}

const logFile = path.join(logsDir, 'app.log');
console.log('Log file path:', logFile);  // Debug log

const logger = {
  info: (...args) => {
    const message = `\n[INFO] ${new Date().toISOString()}\n${args.join(' ')}\n`;
    console.log(message);
    fs.appendFileSync(logFile, message);
  },
  error: (...args) => {
    const message = `\n[ERROR] ${new Date().toISOString()}\n${args.join(' ')}\n`;
    console.error(message);
    fs.appendFileSync(logFile, message);
  },
  debug: (...args) => {
    const message = `\n[DEBUG] ${new Date().toISOString()}\n${args.join(' ')}\n`;
    console.log(message);
    fs.appendFileSync(logFile, message);
  }
};

module.exports = logger; 