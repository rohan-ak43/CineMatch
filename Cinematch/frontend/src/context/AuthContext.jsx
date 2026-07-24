import React, { createContext, useContext, useState, useEffect } from 'react';
import { auth, googleProvider } from '../services/firebase';
import { 
    signInWithPopup, 
    signInWithEmailAndPassword, 
    createUserWithEmailAndPassword, 
    updateProfile,
    signOut
} from 'firebase/auth';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const storedUser = localStorage.getItem('cm_user');
        if (storedUser) {
            setCurrentUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    const exchangeFirebaseToken = async (firebaseUser) => {
        try {
            const idToken = await firebaseUser.getIdToken();
            const res = await api.post('/auth/firebase', { id_token: idToken });
            
            if (res.status === 200) {
                const data = res.data;
                localStorage.setItem('cm_token', data.token);
                localStorage.setItem('cm_user', JSON.stringify(data.user));
                setCurrentUser(data.user);
                return { success: true, message: data.message };
            } else {
                return { success: false, error: res.data.error || 'Authentication failed.' };
            }
        } catch (err) {
            // Dev mode: backend not running — store Firebase user directly
            if (err.name === 'TypeError' || err.code === 'ERR_NETWORK') {
                const u = firebaseUser;
                const demoUser = {
                    id: u.uid,
                    name: u.displayName || (u.email ? u.email.split('@')[0] : 'Demo User'),
                    email: u.email,
                    picture: u.photoURL || null,
                };
                localStorage.setItem('cm_token', 'demo-token');
                localStorage.setItem('cm_user', JSON.stringify(demoUser));
                setCurrentUser(demoUser);
                return { success: true, message: '⚠ API offline — entering demo mode' };
            }
            return { success: false, error: 'Connection error. Is the server running?' };
        }
    };

    const loginWithGoogle = async () => {
        const result = await signInWithPopup(auth, googleProvider);
        return exchangeFirebaseToken(result.user);
    };

    const loginWithEmail = async (email, password) => {
        const cred = await signInWithEmailAndPassword(auth, email, password);
        return exchangeFirebaseToken(cred.user);
    };

    const registerWithEmail = async (name, email, password) => {
        const cred = await createUserWithEmailAndPassword(auth, email, password);
        await updateProfile(cred.user, { displayName: name });
        return exchangeFirebaseToken(cred.user);
    };

    const logout = async () => {
        await signOut(auth);
        localStorage.removeItem('cm_token');
        localStorage.removeItem('cm_user');
        setCurrentUser(null);
    };

    const value = {
        currentUser,
        loginWithGoogle,
        loginWithEmail,
        registerWithEmail,
        logout
    };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};
