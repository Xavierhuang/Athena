const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  firebaseUID: { 
    type: String, 
    required: true, 
    unique: true 
  },
  email: {
    type: String,
    required: true
  },
  name: String,
  gradeLevel: String,
  interests: [String],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('User', userSchema); 