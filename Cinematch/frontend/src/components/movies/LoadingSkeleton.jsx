import React from 'react';

const LoadingSkeleton = ({ count = 10 }) => {
    return (
        <div className="skeleton-grid">
            {Array.from({ length: count }).map((_, i) => (
                <div key={i} className="skeleton-card">
                    <div className="skeleton-poster"></div>
                    <div className="skeleton-body">
                        <div className="skeleton-line"></div>
                        <div className="skeleton-line short"></div>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default LoadingSkeleton;
