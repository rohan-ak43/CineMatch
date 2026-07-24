import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login/Login';
import Dashboard from './pages/Dashboard/Dashboard';
import History from './pages/History/History';

const ProtectedRoute = ({ children }) => {
    const { currentUser } = useAuth();
    if (!currentUser) {
        return <Navigate to="/" replace />;
    }
    return children;
};

const AppRoutes = () => {
    const { currentUser } = useAuth();
    
    return (
        <Routes>
            <Route path="/" element={currentUser ? <Navigate to="/dashboard" replace /> : <Login />} />
            <Route 
                path="/dashboard" 
                element={
                    <ProtectedRoute>
                        <Dashboard />
                    </ProtectedRoute>
                } 
            />
            <Route 
                path="/history" 
                element={
                    <ProtectedRoute>
                        <History />
                    </ProtectedRoute>
                } 
            />
        </Routes>
    );
};

const App = () => {
    return (
        <AuthProvider>
            <BrowserRouter>
                <AppRoutes />
            </BrowserRouter>
        </AuthProvider>
    );
};

export default App;
