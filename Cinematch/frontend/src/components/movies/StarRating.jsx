import React, { useState } from 'react';

const StarRating = ({ rating, onRate }) => {
    const [hover, setHover] = useState(0);

    const labels = {
        0: 'Rate this',
        1: 'Terrible',
        2: 'Poor',
        3: 'Average',
        4: 'Good',
        5: 'Masterpiece'
    };

    const currentDisplay = hover || rating;

    return (
        <div className="star-row">
            {[1, 2, 3, 4, 5].map((star) => (
                <span
                    key={star}
                    className={`star ${star <= rating ? 'rated' : ''} ${star <= hover ? 'hovered' : ''}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        onRate(star);
                    }}
                    onMouseEnter={() => setHover(star)}
                    onMouseLeave={() => setHover(0)}
                >
                    ★
                </span>
            ))}
            <span className={`rate-label ${rating ? 'rated-text' : ''}`}>
                {labels[currentDisplay] || 'Rate this'}
            </span>
        </div>
    );
};

export default StarRating;
