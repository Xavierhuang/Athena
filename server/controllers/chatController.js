const conversationHandler = require('../utils/conversationHandler');
const { OpenAI } = require('openai');
const logger = require('../utils/logger');

// OpenAI Configuration
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// GPT Prompt Templates
const systemPrompt = `You are Athena, an expert in children's activities in New York. 
Provide specific, actionable recommendations based on the child's interests and age.

Format your response with:
1. A brief introduction
2. 3-4 recommendations, each formatted as:

## [Activity Name]
🏠 [Location as clickable Google Maps link]
📝 Description: [Brief description]
✨ Why it's a good match: [Personalized explanation]

Keep descriptions concise and focus on what makes each option uniquely suitable for the child.
Use markdown formatting for better readability.`;

// Utility Functions
function calculateAge(birthdate) {
  const birth = new Date(birthdate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
}

function generatePrompt(userData) {
  let child = userData.children.find(c => c.name === userData.currentChild) || userData.children[0];
  const age = calculateAge(child.birthdate);
  const interests = child.interests ? child.interests.join(', ') : '';
  const specificActivity = child.preferred_activity || '';

  return `
    I need recommendations for activities in ${userData.location} for a ${age}-year-old child named ${child.name}.
    
    Their interests include: ${interests}
    They're specifically interested in: ${specificActivity}
    
    Please provide 3-4 specific activity recommendations that:
    1. Match their age group (${age} years old) and interests (${interests})
    2. Are available in ${userData.location}
    3. Include specific locations and brief descriptions
    4. Consider their specific interest in ${specificActivity}
  `;
}

// GPT Integration
async function generateGPTRecommendations(prompt) {
  try {
    const response = await openai.chat.completions.create({
      model: "o1",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: prompt }
      ]
    });
    return response.choices[0].message.content;
  } catch (error) {
    logger.error('GPT Error:', error);
    throw error;
  }
}

// Main Controller
exports.getRecommendation = async (req, res) => {
  const { question, userData, conversationState } = req.body;
  
  try {
    logger.info('Request:', { question, conversationState, userData });

    const result = conversationHandler.handleConversation(
      question,
      conversationState || 'initial',
      userData
    );

    if (result.nextState === 'recommendations') {
      logger.info('Generating recommendations for:', {
        currentChild: result.userData.currentChild,
        childData: result.userData.children,
        location: result.userData.location
      });

      try {
        const prompt = generatePrompt(result.userData);
        logger.info('Generated prompt:', prompt);
        result.recommendation = await generateGPTRecommendations(prompt);
        logger.info('GPT response:', result.recommendation);
      } catch (gptError) {
        result.recommendation = "I'm having trouble generating recommendations right now. Could you try again?";
      }
    }

    res.json(result);

  } catch (err) {
    logger.error('Server Error:', {
      error: err.message,
      stack: err.stack,
      requestData: req.body
    });
    res.status(500).json({ error: 'Server error' });
  }
}; 