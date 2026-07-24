import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

// ── FIREBASE CONFIGURATION ──
// Fill in your project credentials from https://console.firebase.google.com/
const firebaseConfig = {
    // apiKey: "...",
    // authDomain: "...",
    // projectId: "...",
    // storageBucket: "...",
    // messagingSenderId: "...",
    // appId: "..."
};

// Initialize Firebase with a graceful fallback for empty/missing config.
// This allows the app to run in demo mode even without Firebase credentials.
let auth = null;
let googleProvider = null;

try {
    const hasConfig = firebaseConfig.apiKey && firebaseConfig.projectId;
    if (hasConfig) {
        const app = initializeApp(firebaseConfig);
        auth = getAuth(app);
        googleProvider = new GoogleAuthProvider();
    } else {
        console.warn('Firebase config is empty — running in demo mode. Add your credentials to src/services/firebase.js');
    }
} catch (err) {
    console.warn('Firebase initialization failed — running in demo mode.', err.message);
}

export { auth, googleProvider };
