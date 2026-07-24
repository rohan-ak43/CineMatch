import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Components.css';

const Navbar = () => {
    const { currentUser, logout } = useAuth();

    return (
        <header className="topbar">
            <div className="topbar-logo">CINEMATCH</div>
            <nav className="topbar-nav">
                <NavLink 
                    to="/dashboard" 
                    className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                >
                    Discover
                </NavLink>
                <div className="nav-sep"></div>
                <NavLink 
                    to="/history" 
                    className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                >
                    History
                </NavLink>
                <div className="nav-sep"></div>
                
                {currentUser && (
                    <div className="user-badge" style={{ marginRight: '8px', marginLeft: '8px' }}>
                        <div className="user-avatar">
                            {currentUser.picture ? (
                                <img src={currentUser.picture} alt="Avatar" style={{width: '100%', height: '100%', borderRadius: '50%'}} />
                            ) : (
                                currentUser.name?.charAt(0).toUpperCase() || 'U'
                            )}
                        </div>
                        <div className="user-name">{currentUser.name}</div>
                    </div>
                )}
                
                <button className="btn-logout" onClick={logout}>Exit</button>
            </nav>
        </header>
    );
};

export default Navbar;
