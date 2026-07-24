import React, { useState, useEffect } from 'react';

const ReviewModal = ({ isOpen, onClose, movie, onSave, isSaving }) => {
    const [text, setText] = useState('');

    useEffect(() => {
        if (isOpen && movie) {
            setText(movie.review_text || '');
        }
    }, [isOpen, movie]);

    if (!isOpen || !movie) return null;

    return (
        <div className={`modal-overlay ${isOpen ? 'open' : ''}`}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <div className="modal-title">Write a Review</div>
                <div className="modal-movie">{movie.title}</div>
                
                <textarea 
                    className="modal-textarea" 
                    placeholder="What did you think of the film?" 
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                />
                
                {movie.sentiment && movie.sentiment !== 'none' && (
                    <div className="sentiment-result show">
                        <div className="sentiment-emoji">
                            {movie.sentiment === 'positive' ? '😊' : movie.sentiment === 'negative' ? '😞' : '😐'}
                        </div>
                        <div className="sentiment-info">
                            <span className={`sentiment-label ${movie.sentiment}`}>
                                {movie.sentiment === 'positive' ? 'Positive' : movie.sentiment === 'negative' ? 'Negative' : 'Neutral'}
                            </span>
                            <div className="sentiment-bar-wrap">
                                <div className="sentiment-bar">
                                    <div className={`sentiment-fill ${movie.sentiment}`} style={{ width: '100%' }}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
                
                <div className="modal-actions">
                    <button className="btn-cancel" onClick={onClose}>Cancel</button>
                    <button className="btn-save" onClick={() => onSave(text)} disabled={isSaving}>
                        {isSaving ? 'Saving...' : 'Save Review'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ReviewModal;
