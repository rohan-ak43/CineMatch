import React from 'react';
import StarRating from './StarRating';

const GENRE_EMOJI = {
    Action: '⚔️', Adventure: '🗺️', Animation: '✨', Comedy: '😂', Crime: '🔎',
    Drama: '🎭', Fantasy: '🧙', Horror: '👻', Mystery: '🔍', Romance: '💕',
    'Sci-Fi': '🚀', Thriller: '🔪', Children: '🧸'
};

const MovieCard = ({ movie, onRate, onReview }) => {
    const genres = (movie.genre || '').split('|');
    const primaryGenre = genres[0];
    const emoji = GENRE_EMOJI[primaryGenre] || '🎬';

    // Generative poster gradient based on ID
    const hue1 = (movie.movie_id * 137) % 360;
    const hue2 = (movie.movie_id * 73) % 360;
    const gradient = `linear-gradient(135deg, hsl(${hue1}, 40%, 15%), hsl(${hue2}, 30%, 8%))`;

    return (
        <div className="movie-card">
            <div className="card-poster">
                <div className="card-poster-inner" style={{ background: gradient }}>
                    <div className="card-poster-art"></div>
                    <div className="card-poster-genre-icon">{emoji}</div>
                </div>
                {movie.predicted_score && (
                    <div className="card-score-badge">{movie.predicted_score}% Match</div>
                )}
            </div>
            
            <div className="card-body">
                <div className="card-title" title={movie.title}>{movie.title}</div>
                <div className="card-genres">{genres.slice(0, 3).join(' · ')}</div>
                
                <StarRating 
                    rating={movie.rating || 0} 
                    onRate={(val) => onRate(movie.movie_id, val)} 
                />
                
                <button 
                    className="btn-review" 
                    onClick={(e) => {
                        e.stopPropagation();
                        onReview(movie);
                    }}
                >
                    {movie.review_text ? 'Edit Review' : 'Write Review'}
                </button>
            </div>
        </div>
    );
};

export default React.memo(MovieCard);
