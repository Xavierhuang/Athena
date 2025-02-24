const User = require('../models/user');

exports.getProfile = async (req, res) => {
  try {
    const firebaseUID = req.user.uid;
    const user = await User.findOne({ firebaseUID });
    
    if (!user) {
      return res.status(404).json({ error: 'User profile not found' });
    }
    
    res.json(user);
  } catch (err) {
    console.error('Profile fetch error:', err);
    res.status(500).json({ error: 'Failed to fetch profile' });
  }
};

exports.updateProfile = async (req, res) => {
  try {
    const firebaseUID = req.user.uid;
    const { name, email, gradeLevel, interests } = req.body;

    let user = await User.findOne({ firebaseUID });
    
    if (!user) {
      user = new User({
        firebaseUID,
        email: email || req.user.email,
        name,
        gradeLevel,
        interests
      });
    } else {
      user.name = name || user.name;
      user.email = email || user.email;
      user.gradeLevel = gradeLevel || user.gradeLevel;
      user.interests = interests || user.interests;
    }

    await user.save();
    res.json(user);
  } catch (err) {
    console.error('Profile update error:', err);
    res.status(500).json({ error: 'Failed to update profile' });
  }
}; 