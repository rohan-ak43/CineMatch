import React from 'react';

const StatsCards = ({ total, rated, avg, reviews }) => {
    return (
        <div className="stats-row">
            <div className="stat-box">
                <div className="stat-val">{total}</div>
                <div className="stat-label">Films Watched</div>
            </div>
            <div className="stat-box">
                <div className="stat-val">{rated}</div>
                <div className="stat-label">Films Rated</div>
            </div>
            <div className="stat-box">
                <div className="stat-val">{avg !== '—' ? `${avg}★` : '—'}</div>
                <div className="stat-label">Avg Rating</div>
            </div>
            <div className="stat-box">
                <div className="stat-val">{reviews}</div>
                <div className="stat-label">Reviews Written</div>
            </div>
        </div>
    );
};

export default StatsCards;
