import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Goal(Enum):
    FIND_ACTIVITIES = "find_activities"
    # Future goals can be added here
    
@dataclass
class Child:
    name: str
    birthdate: datetime
    interests: List[str]
    preferred_activity_type: Optional[str] = None

@dataclass
class Parent:
    location: str
    children: List[Child]
    has_account: bool = False
    bookmarked_activities: List[str] = None

class ConversationFlowTutorial:
    """
    Tutorial demonstrating how to build a conversational recommendation system
    """
    
    def __init__(self):
        self.logger = logger
        # Load activities data
        with open('activities_data.json', 'r') as f:
            self.activities = json.load(f)
    
    def lesson_1_user_data_collection(self):
        """
        Lesson 1: Collecting User Information
        Shows how to gather and structure user data through conversation
        """
        self.logger.info("\n=== Lesson 1: User Data Collection ===")
        
        try:
            # Simulate conversation flow
            self.logger.info("1. Goal Selection:")
            goal = Goal.FIND_ACTIVITIES  # MVP default
            self.logger.info(f"Selected goal: {goal.value}")
            
            # Collect basic information
            self.logger.info("\n2. Basic Information Collection:")
            location = input("Where do you live? ")
            num_children = int(input("How many children do you have? "))
            
            # Collect children information
            children = []
            for i in range(num_children):
                self.logger.info(f"\nChild {i+1} Information:")
                name = input(f"Child {i+1} name: ")
                birthdate = input(f"Child {i+1} birthdate (YYYY-MM-DD): ")
                interests = input(f"What activities does {name} enjoy? (comma-separated): ").split(',')
                activity_type = input(f"Looking for specific activity type for {name}? ")
                
                child = Child(
                    name=name,
                    birthdate=datetime.strptime(birthdate, '%Y-%m-%d'),
                    interests=[i.strip() for i in interests],
                    preferred_activity_type=activity_type
                )
                children.append(child)
            
            # Create parent profile
            parent = Parent(location=location, children=children)
            return parent
            
        except Exception as e:
            self.logger.error(f"Error in lesson 1: {str(e)}")
    
    def lesson_2_account_management(self, parent: Parent):
        """
        Lesson 2: Account Management
        Demonstrates account verification and creation flow
        """
        self.logger.info("\n=== Lesson 2: Account Management ===")
        
        try:
            if not parent.has_account:
                self.logger.info("Account required for personalized recommendations")
                create_account = input("Would you like to create an account? (y/n): ")
                
                if create_account.lower() == 'y':
                    # Simulate account creation
                    parent.has_account = True
                    self.logger.info("Account created successfully!")
                else:
                    self.logger.info("Account required to proceed")
                    return None
            
            return parent
            
        except Exception as e:
            self.logger.error(f"Error in lesson 2: {str(e)}")
    
    def lesson_3_recommendation_engine(self, parent: Parent):
        """
        Lesson 3: Generating Recommendations
        Shows how to generate personalized activity recommendations
        """
        self.logger.info("\n=== Lesson 3: Recommendation Engine ===")
        
        try:
            recommendations = {}
            
            for child in parent.children:
                child_recommendations = []
                
                # Filter by location
                local_activities = [
                    activity for activity in self.activities
                    if parent.location.lower() in activity['location']['city'].lower()
                ]
                
                # Match interests and activity types
                for activity in local_activities:
                    # Simple matching logic for demonstration
                    if (any(interest.lower() in activity['description'].lower() 
                           for interest in child.interests) or
                        (child.preferred_activity_type and 
                         child.preferred_activity_type.lower() in activity['description'].lower())):
                        child_recommendations.append(activity)
                
                recommendations[child.name] = child_recommendations
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error in lesson 3: {str(e)}")
    
    def lesson_4_user_interaction(self, parent: Parent, recommendations: Dict):
        """
        Lesson 4: Handling User Interactions
        Demonstrates how to handle bookmarks and refinements
        """
        self.logger.info("\n=== Lesson 4: User Interaction ===")
        
        try:
            for child_name, activities in recommendations.items():
                self.logger.info(f"\nRecommendations for {child_name}:")
                
                for i, activity in enumerate(activities, 1):
                    self.logger.info(f"\n{i}. {activity['name']}")
                    self.logger.info(f"   Location: {activity['location']['name']}")
                    
                    # Simulate bookmark functionality
                    bookmark = input(f"Bookmark this activity? (y/n): ")
                    if bookmark.lower() == 'y':
                        if not parent.bookmarked_activities:
                            parent.bookmarked_activities = []
                        parent.bookmarked_activities.append(activity['name'])
                    
                    # Get refinement feedback
                    feedback = input("Any additional preferences? (Enter to skip): ")
                    if feedback:
                        # Here you would implement logic to refine recommendations
                        self.logger.info("Refining recommendations based on feedback...")
            
            return parent
            
        except Exception as e:
            self.logger.error(f"Error in lesson 4: {str(e)}")

def run_tutorial():
    """Run the complete tutorial"""
    tutorial = ConversationFlowTutorial()
    
    # Lesson 1: Collect user data
    parent = tutorial.lesson_1_user_data_collection()
    if not parent:
        return
    
    # Lesson 2: Handle account
    parent = tutorial.lesson_2_account_management(parent)
    if not parent:
        return
    
    # Lesson 3: Generate recommendations
    recommendations = tutorial.lesson_3_recommendation_engine(parent)
    if not recommendations:
        return
    
    # Lesson 4: Handle user interaction
    tutorial.lesson_4_user_interaction(parent, recommendations)

if __name__ == "__main__":
    run_tutorial() 