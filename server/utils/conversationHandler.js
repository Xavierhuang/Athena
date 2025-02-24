const fs = require('fs');
const path = require('path');

const ConversationState = {
  INITIAL: "initial",
  LOCATION: "location",
  NUM_CHILDREN: "num_children",
  SELECT_CHILD: "select_child",
  CHILD_DETAILS: "child_details",
  INTERESTS: "interests",
  RECOMMENDATIONS: "recommendations",
  NEXT_CHILD: "next_child",
  SIGN_IN_PROMPT: "sign_in_prompt"
};

class ConversationHandler {
  constructor() {
    this.conversationFlow = {
      [ConversationState.INITIAL]: {
        message: "Hi! I'm Athena, your personal guide to unlocking the best educational opportunities, activities, and services for your child here in New York. Tell me a bit about your child—like their age, interests, or what you're hoping to find—and I'll get started finding the perfect options for you!\n\nFirst, where do you live?",
        nextState: ConversationState.LOCATION,
        expectedData: 'location'
      },
      [ConversationState.LOCATION]: {
        message: "How many children do you have?",
        nextState: ConversationState.NUM_CHILDREN,
        expectedData: 'num_children'
      },
      [ConversationState.NUM_CHILDREN]: {
        message: "What are their names and birthdates? (e.g., 'John, 2015-06-15')",
        nextState: ConversationState.SELECT_CHILD,
        expectedData: 'child_info'
      },
      [ConversationState.SELECT_CHILD]: {
        message: "Who would you like to find activities for first?",
        nextState: ConversationState.CHILD_DETAILS,
        expectedData: 'selected_child'
      },
      [ConversationState.CHILD_DETAILS]: {
        message: "What activities does {child_name} enjoy? (e.g., sports, art, music)",
        nextState: ConversationState.INTERESTS,
        expectedData: 'interests'
      },
      [ConversationState.INTERESTS]: {
        message: "Are you looking for a specific type of activity for {child_name}?",
        nextState: ConversationState.RECOMMENDATIONS,
        expectedData: 'preferred_activity'
      },
      [ConversationState.RECOMMENDATIONS]: {
        message: "Here are some activities I found for {child_name}. Would you like to find activities for another child?",
        nextState: ConversationState.NEXT_CHILD,
        expectedData: 'feedback'
      },
      [ConversationState.NEXT_CHILD]: {
        message: "Which child would you like to find activities for next?",
        nextState: ConversationState.CHILD_DETAILS,
        expectedData: 'selected_child'
      },
      [ConversationState.SIGN_IN_PROMPT]: {
        message: "Would you like to save these recommendations? Sign in or create an account to access them later!",
        nextState: ConversationState.SIGN_IN_PROMPT,
        expectedData: 'sign_in_response'
      }
    };
  }

  handleConversation(userInput, currentState, userData = {}) {
    try {
      console.log('Starting conversation handler:', { userInput, currentState, userData });

      if (userInput === 'start') {
        return {
          recommendation: this.conversationFlow[ConversationState.INITIAL].message,
          nextState: ConversationState.INITIAL,
          userData: {}
        };
      }

      const updatedData = this.processResponse(userInput, currentState, userData);
      console.log('Processed response:', { updatedData, currentState });

      if (!updatedData) {
        const flow = this.conversationFlow[currentState];
        return {
          recommendation: `I didn't understand that. ${flow.message}`,
          nextState: currentState,
          userData
        };
      }

      const nextState = this.getNextState(currentState, updatedData);
      const nextQuestion = this.getNextQuestion(nextState, updatedData);

      if (nextState === ConversationState.RECOMMENDATIONS) {
        return {
          recommendation: nextQuestion.message,
          nextState: nextState,
          userData: updatedData
        };
      }

      return {
        recommendation: nextQuestion.message,
        nextState: nextState,
        userData: updatedData
      };
    } catch (error) {
      console.error('Conversation handler error:', error);
      return {
        recommendation: "I'm having trouble processing your request. Could you try again?",
        nextState: currentState,
        userData
      };
    }
  }

  getNextState(currentState, userData) {
    console.log('\n=== Getting Next State ===');
    console.log('Current State:', currentState);
    console.log('User Data:', JSON.stringify(userData, null, 2));

    switch (currentState) {
      case ConversationState.INITIAL:
        return ConversationState.LOCATION;
      case ConversationState.LOCATION:
        return ConversationState.NUM_CHILDREN;
      case ConversationState.NUM_CHILDREN:
        return userData.children.length > 1 ? 
          ConversationState.SELECT_CHILD : 
          ConversationState.CHILD_DETAILS;
      case ConversationState.SELECT_CHILD:
        return ConversationState.CHILD_DETAILS;
      case ConversationState.CHILD_DETAILS:
        return ConversationState.INTERESTS;
      case ConversationState.INTERESTS:
        return ConversationState.RECOMMENDATIONS;
      case ConversationState.RECOMMENDATIONS:
        if (userData.children.length > 1 && 
            (!userData.processedChildren || 
             userData.processedChildren.length < userData.children.length)) {
          return ConversationState.NEXT_CHILD;
        }
        return ConversationState.RECOMMENDATIONS;
      case ConversationState.NEXT_CHILD:
        return ConversationState.CHILD_DETAILS;
      default:
        return currentState;
    }
  }

  getNextQuestion(currentState, userData) {
    const flow = this.conversationFlow[currentState];
    if (!flow) {
      return {
        message: "I'll help you find some activities based on what you've told me.",
        nextState: ConversationState.RECOMMENDATIONS
      };
    }

    let message = flow.message;
    if (message.includes('{child_name}') && userData.children?.length > 0) {
      const currentChild = userData.children[userData.children.length - 1];
      message = message.replace(/\{child_name\}/g, currentChild.name);
    }

    return {
      message,
      nextState: flow.nextState
    };
  }

  processResponse(response, currentState, userData) {
    console.log('\n=== Processing Response ===');
    console.log('Current State:', currentState);
    console.log('Response:', response);
    console.log('User Data:', JSON.stringify(userData, null, 2));

    const updatedData = { ...userData };

    try {
      switch (currentState) {
        case ConversationState.INITIAL:
          if (response.trim()) {
            updatedData.location = response.trim();
            return updatedData;
          }
          return null;

        case ConversationState.LOCATION:
          const numChildren = parseInt(response.trim());
          if (isNaN(numChildren) || numChildren < 1) return null;
          updatedData.num_children = numChildren;
          updatedData.children = [];
          return updatedData;

        case ConversationState.NUM_CHILDREN:
          try {
            const [name, birthdate] = response.split(',').map(x => x.trim());
            if (!name || !birthdate) return null;
            updatedData.children = [...(updatedData.children || []), { name, birthdate }];
            return updatedData;
          } catch (e) {
            return null;
          }

        case ConversationState.SELECT_CHILD:
        case ConversationState.NEXT_CHILD:
          const selectedChild = updatedData.children.find(
            child => child.name.toLowerCase() === response.toLowerCase()
          );
          if (selectedChild) {
            updatedData.currentChild = selectedChild.name;
            return updatedData;
          }
          return null;

        case ConversationState.CHILD_DETAILS:
          if (!updatedData.children?.length) return null;
          const currentChild = updatedData.children[updatedData.children.length - 1];
          // Store general interests
          currentChild.interests = response.split(',').map(x => x.trim());
          console.log('Stored interests:', currentChild.interests);
          return updatedData;

        case ConversationState.INTERESTS:
          if (!updatedData.children?.length) {
            console.log('No children found in user data');
            return null;
          }
          const lastChild = updatedData.children[updatedData.children.length - 1];
          console.log('Processing specific activity for child:', lastChild);
          
          // Make sure we keep the previous interests and add the specific activity
          if (!lastChild.interests) {
            lastChild.interests = [];
          }
          lastChild.preferred_activity = response.trim();
          
          console.log('Updated child data:', {
            name: lastChild.name,
            interests: lastChild.interests,
            preferred_activity: lastChild.preferred_activity
          });
          return updatedData;

        case ConversationState.RECOMMENDATIONS:
          if (response.toLowerCase() === 'no' || updatedData.complete) {
            return {
              ...updatedData,
              nextState: ConversationState.SIGN_IN_PROMPT
            };
          }
          if (response.toLowerCase() === 'yes' && 
              updatedData.children.length > 1 && 
              !updatedData.processedChildren?.includes(updatedData.currentChild)) {
            // Mark current child as processed
            updatedData.processedChildren = [
              ...(updatedData.processedChildren || []),
              updatedData.currentChild
            ];
            // If there are unprocessed children, go to NEXT_CHILD state
            if (updatedData.processedChildren.length < updatedData.children.length) {
              return updatedData;
            }
          }
          // Otherwise, end the conversation
          updatedData.complete = true;
          return updatedData;

        default:
          return updatedData;
      }
    } catch (error) {
      console.error('Error in processResponse:', error);
      return null;
    }
  }
}

module.exports = new ConversationHandler();