import { initializeApp } from 'firebase/app';
import { getAnalytics } from 'firebase/analytics';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyCCzrgsct17HP4eYg7wTbwrj-0BJPxDj4E",
  authDomain: "athena-20c69.firebaseapp.com",
  projectId: "athena-20c69",
  storageBucket: "athena-20c69.firebasestorage.app",
  messagingSenderId: "990885879192",
  appId: "1:990885879192:web:3ae26479756f4d4de41fed",
  measurementId: "G-XGNRRWZWGG"
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);

export { auth }; 