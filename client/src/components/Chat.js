import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import '../styles/Chat.css';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [conversationState, setConversationState] = useState('initial');
  const [userData, setUserData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [showSignInModal, setShowSignInModal] = useState(false);

  // Add input ref
  const inputRef = useRef(null);

  // Start conversation when component mounts
  useEffect(() => {
    console.log("Starting conversation...");
    initiateConversation();
  }, []);

  useEffect(() => {
    if (conversationState === 'sign_in_prompt') {
      setShowSignInModal(true);
    }
  }, [conversationState]);

  // Add new effect to handle focus after loading
  useEffect(() => {
    if (!isLoading) {
      // Small delay to ensure DOM is updated
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isLoading]);

  const initiateConversation = async () => {
    setIsLoading(true);
    try {
      console.log("Making initial request...");
      const response = await axios.post('http://localhost:3001/api/chat', {
        question: 'start',
        conversationState: 'initial',
        userData: {}
      });

      console.log("Got response:", response.data);
      setMessages([{
        type: 'assistant',
        content: response.data.recommendation
      }]);
      setConversationState(response.data.nextState);
      setUserData(response.data.userData);
    } catch (error) {
      console.error('Error starting conversation:', error);
    }
    setIsLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const newMessages = [...messages, {
      type: 'user',
      content: userInput
    }];
    setMessages(newMessages);
    setUserInput('');
    setIsLoading(true);

    try {
      const response = await axios.post('http://localhost:3001/api/chat', {
        question: userInput,
        conversationState,
        userData
      });

      console.log('Sending:', { userInput, conversationState, userData });
      console.log('Received:', response.data);

      setMessages([...newMessages, {
        type: 'assistant',
        content: response.data.recommendation
      }]);
      setConversationState(response.data.nextState);
      setUserData(response.data.userData);
    } catch (error) {
      console.error('Error:', error);
    }
    setIsLoading(false);
  };

  const SignInModal = () => (
    <div className="modal">
      <div className="modal-content">
        <h2>Save Your Recommendations</h2>
        <p>Sign in or create an account to save these recommendations and access them later!</p>
        <div className="modal-buttons">
          <button onClick={() => window.location.href = '/login'}>Sign In</button>
          <button onClick={() => window.location.href = '/signup'}>Create Account</button>
          <button onClick={() => setShowSignInModal(false)}>Maybe Later</button>
        </div>
      </div>
    </div>
  );

  const Message = ({ text, sender }) => (
    <div className={`message ${sender === 'You' ? 'user-message' : 'athena-message'}`}>
      <div className="message-sender">{sender}:</div>
      <div className="message-text">{text}</div>
    </div>
  );

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>Athena Education Assistant</h1>
        <p>
          Your personal guide to discovering the perfect educational opportunities 
          in New York. From after-school programs to academic enrichment, 
          we'll help your child reach their full potential.
        </p>
      </div>
      
      <div className="chat-messages">
        {messages.map((message, index) => (
          <Message key={index} text={message.content} sender={message.type === 'assistant' ? 'Athena' : 'You'} />
        ))}
        {isLoading && <div className="loading">Athena is thinking...</div>}
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <input
          ref={inputRef}
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your response..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !userInput.trim()}>
          Send
        </button>
      </form>

      {showSignInModal && <SignInModal />}
    </div>
  );
};

export default Chat; 