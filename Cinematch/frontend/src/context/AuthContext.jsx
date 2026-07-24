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

// ── DEMO MODE ──
// Used when Firebase is not configured (empty/missing config)
const DEMO_USER = {
    id: 'demo-user',
    name: 'Demo User',
    email: 'demo@cinematch.app',
    picture: null,
};

const isDemoMode = !auth;

export const AuthProvider = ({ children }) => {
    const [currentUser, setCurrentUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const storedUser = localStorage.getItem('cm_user');
        if (storedUser) {
            try {
                setCurrentUser(JSON.parse(storedUser));
            } catch {
                localStorage.removeItem('cm_user');
            }
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
            // Backend not running — store Firebase user info directly for demo
            if (err.code === 'ERR_NETWORK' || err.name === 'TypeError') {
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
        if (isDemoMode) {
            localStorage.setItem('cm_token', 'demo-token');
            localStorage.setItem('cm_user', JSON.stringify(DEMO_USER));
            setCurrentUser(DEMO_USER);
            return { success: true, message: '⚠ Demo mode — Firebase not configured' };
        }
        try {
            const result = await signInWithPopup(auth, googleProvider);
            return exchangeFirebaseToken(result.user);
        } catch (err) {
            if (err.code === 'auth/popup-closed-by-user') {
                return { success: false, error: null };
            }
            return { success: false, error: err.message || 'Google sign-in failed.' };
        }
    };

    const loginWithEmail = async (email, password) => {
        if (isDemoMode) {
            const user = { ...DEMO_USER, email, name: email.split('@')[0] };
            localStorage.setItem('cm_token', 'demo-token');
            localStorage.setItem('cm_user', JSON.stringify(user));
            setCurrentUser(user);
            return { success: true, message: '⚠ Demo mode — Firebase not configured' };
        }
        const cred = await signInWithEmailAndPassword(auth, email, password);
        return exchangeFirebaseToken(cred.user);
    };

    const registerWithEmail = async (name, email, password) => {
        if (isDemoMode) {
            const user = { ...DEMO_USER, name, email };
            localStorage.setItem('cm_token', 'demo-token');
            localStorage.setItem('cm_user', JSON.stringify(user));
            setCurrentUser(user);
            return { success: true, message: '⚠ Demo mode — Firebase not configured' };
        }
        const cred = await createUserWithEmailAndPassword(auth, email, password);
        await updateProfile(cred.user, { displayName: name });
        return exchangeFirebaseToken(cred.user);
    };

    const logout = async () => {
        if (auth) {
            try { await signOut(auth); } catch {}
        }
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
