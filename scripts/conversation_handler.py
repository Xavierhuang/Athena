import json
import logging
from pathlib import Path
from typing import Dict, List
from enum import Enum
import sys

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConversationState(Enum):
    INITIAL = "initial"
    LOCATION = "location"
    NUM_CHILDREN = "num_children"
    CHILD_DETAILS = "child_details"
    INTERESTS = "interests"
    RECOMMENDATIONS = "recommendations"

class ConversationHandler:
    """
    Handles the conversation flow for the Athena activity recommendation system.
    Works with the existing OpenAI chat implementation.
    """
    
    def __init__(self):
        # Load activities data
        self.activities_file = Path('activities_data.json')
        if self.activities_file.exists():
            with open(self.activities_file, 'r') as f:
                self.activities = json.load(f)
        else:
            logger.warning("No activities data found")
            self.activities = []

        # Define preset questions and flow
        self.conversation_flow = {
            ConversationState.INITIAL: {
                'message': "Hi! I'm Athena, your activity advisor. I'll help you find the perfect activities for your children! First, where do you live?",
                'next_state': ConversationState.LOCATION,
                'expected_data': 'location'
            },
            ConversationState.LOCATION: {
                'message': "Great! How many children do you have?",
                'next_state': ConversationState.NUM_CHILDREN,
                'expected_data': 'num_children'
            },
            ConversationState.NUM_CHILDREN: {
                'message': "Please tell me your child's name and birthdate (e.g., 'John, 2015-06-15')",
                'next_state': ConversationState.CHILD_DETAILS,
                'expected_data': 'child_info'
            },
            ConversationState.CHILD_DETAILS: {
                'message': "What activities does {child_name} enjoy? (e.g., sports, art, music)",
                'next_state': ConversationState.INTERESTS,
                'expected_data': 'interests'
            },
            ConversationState.INTERESTS: {
                'message': "Are you looking for any specific type of activity for {child_name}?",
                'next_state': ConversationState.RECOMMENDATIONS,
                'expected_data': 'preferred_activity'
            }
        }

    def format_system_prompt(self, conversation_state: ConversationState = ConversationState.INITIAL, user_data: Dict = None) -> str:
        """
        Creates the system prompt based on conversation state
        """
        base_prompt = (
            "You are Athena, an intelligent academic advisor specializing in extracurricular activities. "
            "You communicate warmly and clearly in English. "
            "\nCurrent goal: Finding activities for children (MVP focus)"
        )

        # Add state-specific instructions
        state_prompts = {
            ConversationState.INITIAL: (
                "\nStart by saying: 'I'm here to help you find activities for your children!' "
                "Then ask: 'Where do you live?'"
            ),
            ConversationState.LOCATION: (
                "\nNow that you have the location, ask: 'How many children do you have?'"
            ),
            ConversationState.NUM_CHILDREN: (
                "\nAsk for each child's name and birthdate one at a time: "
                "'Please tell me the name and birthdate of your first child.'"
            ),
            ConversationState.CHILD_DETAILS: (
                "\nFor each child, ask about their interests: "
                "'What activities does [child_name] enjoy?' "
                "Then ask: 'Are you looking for any specific type of activity for [child_name]?'"
            ),
            ConversationState.RECOMMENDATIONS: (
                "\nBased on the collected information, provide personalized recommendations "
                "from the available activities. Format them clearly and ask if they'd like to "
                "bookmark any activities or get different recommendations."
            )
        }

        base_prompt += state_prompts.get(conversation_state, "")

        # Add available activities context
        if self.activities:
            base_prompt += f"\n\nYou have access to {len(self.activities)} activities in the database."

        # Add current user data context
        if user_data:
            base_prompt += "\n\nCurrent user information:"
            if user_data.get('location'):
                base_prompt += f"\nLocation: {user_data['location']}"
            if user_data.get('children'):
                base_prompt += f"\nNumber of children: {len(user_data['children'])}"
                for child in user_data['children']:
                    base_prompt += f"\n- {child['name']} (born: {child['birthdate']})"
                    if child.get('interests'):
                        base_prompt += f"\n  Interests: {', '.join(child['interests'])}"
                    if child.get('preferred_activity'):
                        base_prompt += f"\n  Looking for: {child['preferred_activity']}"

        return base_prompt

    def determine_next_state(self, current_state: ConversationState, user_data: Dict) -> ConversationState:
        """
        Determines the next conversation state based on current state and user data
        """
        if current_state == ConversationState.INITIAL and user_data.get('location'):
            return ConversationState.LOCATION
        elif current_state == ConversationState.LOCATION and user_data.get('num_children'):
            return ConversationState.NUM_CHILDREN
        elif current_state == ConversationState.NUM_CHILDREN and user_data.get('children'):
            return ConversationState.CHILD_DETAILS
        elif current_state == ConversationState.CHILD_DETAILS:
            # Check if all children have interests and preferred activities
            children = user_data.get('children', [])
            all_complete = all(
                child.get('interests') and child.get('preferred_activity')
                for child in children
            )
            if all_complete:
                return ConversationState.RECOMMENDATIONS
        return current_state

    def get_next_question(self, current_state: ConversationState, user_data: Dict) -> Dict:
        """Get the next question based on conversation state and user data"""
        flow = self.conversation_flow.get(current_state)
        if not flow:
            return {
                'message': "I'll help you find some activities based on what you've told me.",
                'next_state': ConversationState.RECOMMENDATIONS
            }

        message = flow['message']
        
        # Format message with child's name if needed
        if '{child_name}' in message and user_data.get('children'):
            current_child = user_data['children'][-1]
            message = message.format(child_name=current_child['name'])

        return {
            'message': message,
            'next_state': flow['next_state']
        }

    def process_response(self, response: str, current_state: ConversationState, user_data: Dict) -> Dict:
        """Process user response and return updated data"""
        updated_data = user_data.copy()
        
        if current_state == ConversationState.INITIAL:
            updated_data['location'] = response.strip()
            
        elif current_state == ConversationState.LOCATION:
            try:
                updated_data['num_children'] = int(response.strip())
                updated_data['children'] = []
            except ValueError:
                return None
            
        elif current_state == ConversationState.NUM_CHILDREN:
            try:
                name, birthdate = [x.strip() for x in response.split(',')]
                child = {'name': name, 'birthdate': birthdate}
                updated_data['children'] = updated_data.get('children', []) + [child]
            except ValueError:
                return None
            
        elif current_state == ConversationState.CHILD_DETAILS:
            if updated_data.get('children'):
                current_child = updated_data['children'][-1]
                current_child['interests'] = [x.strip() for x in response.split(',')]
            
        elif current_state == ConversationState.INTERESTS:
            if updated_data.get('children'):
                current_child = updated_data['children'][-1]
                current_child['preferred_activity'] = response.strip()

        return updated_data

    def generate_recommendations(self, user_data: Dict) -> List[Dict]:
        """
        Filters activities based on user data
        """
        recommendations = []
        
        # Add recommendation logic here
        # This would feed into the OpenAI prompt
        
        return recommendations

    def format_recommendations(self, recommendations: List[Dict]) -> str:
        """
        Formats recommendations for the chat response
        """
        if not recommendations:
            return "I couldn't find any matching activities. Let me ask some questions to better understand your needs."
            
        response = "Here are some recommendations:\n\n"
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. {rec['name']}\n"
            response += f"   Location: {rec['location']['name']}\n"
            if rec.get('description'):
                response += f"   {rec['description'][:100]}...\n"
            response += "\n"
            
        response += "\nWould you like to bookmark any of these activities? Or shall I refine the recommendations?"
        return response

    def handle_bookmark(self, activity_id: str, user_id: str) -> bool:
        """
        Handles bookmarking an activity for a user
        """
        # Add bookmark logic here
        # This would integrate with your existing system
        return True

    def refine_recommendations(self, feedback: str, previous_recommendations: List[Dict]) -> List[Dict]:
        """
        Refines recommendations based on user feedback
        """
        # Add refinement logic here
        # This would feed into the OpenAI prompt
        return []

    def handle_conversation(self, user_input: str, current_state: str, user_data: Dict) -> Dict:
        """Main handler for conversation flow"""
        try:
            # Convert string state to enum
            current_state = ConversationState(current_state)
            
            if user_input == 'start':
                # Initial conversation
                next_question = self.get_next_question(ConversationState.INITIAL, {})
                print("Returning initial response:", {  # Add debug logging
                    'message': next_question['message'],
                    'nextState': next_question['next_state'].value,
                    'userData': {}
                })
                return {
                    'message': next_question['message'],
                    'nextState': next_question['next_state'].value,
                    'userData': {}
                }
                
            # Process user response
            updated_data = self.process_response(user_input, current_state, user_data)
            if updated_data is None:
                return {
                    'recommendation': "I didn't understand that. " + 
                                    self.conversation_flow[current_state]['message'],
                    'nextState': current_state.value,
                    'userData': user_data
                }
                
            # Get next question
            next_question = self.get_next_question(current_state, updated_data)
            
            return {
                'recommendation': next_question['message'],
                'nextState': next_question['next_state'].value,
                'userData': updated_data
            }
            
        except Exception as e:
            logger.error(f"Error handling conversation: {str(e)}")
            return {
                'recommendation': "I'm having trouble understanding. Could you try rephrasing that?",
                'nextState': current_state,
                'userData': user_data
            }

if __name__ == "__main__":
    # Get arguments passed from Node.js
    user_data = json.loads(sys.argv[1])
    current_state = sys.argv[2]
    
    # Create handler and process request
    handler = ConversationHandler()
    result = handler.handle_conversation('start', current_state, user_data)
    
    # Print result as JSON (this is what PythonShell reads)
    print(json.dumps(result)) 