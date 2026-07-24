import React from 'react';

const GENRE_EMOJI = {
    Action: '⚔️', Adventure: '🗺️', Animation: '✨', Comedy: '😂', Crime: '🔎',
    Drama: '🎭', Fantasy: '🧙', Horror: '👻', Mystery: '🔍', Romance: '💕',
    'Sci-Fi': '🚀', Thriller: '🔪', Children: '🧸'
};

const formatDate = (iso) => {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
};

const starsHTML = (n) => {
    n = parseInt(n) || 0;
    return (
        <>
            {'★'.repeat(n)}
            <span className="star-empty">{'★'.repeat(5 - n)}</span>
        </>
    );
};

const HistoryTable = ({ history }) => {
    return (
        <table className="history-table">
            <thead>
                <tr>
                    <th>Film</th>
                    <th>Rating</th>
                    <th>Sentiment</th>
                    <th>Watched</th>
                </tr>
            </thead>
            <tbody>
                {history.map((item, idx) => {
                    const genres = (item.genre || '').split('|');
                    const emoji = GENRE_EMOJI[genres[0]] || '🎬';
                    const sentiment = item.sentiment || 'none';
                    const sentimentLabels = { positive: '😊 Positive', negative: '😞 Negative', neutral: '😐 Neutral', none: '— Not reviewed' };

                    return (
                        <tr key={item.movie_id || idx} style={{ animationDelay: `${idx * 0.04}s` }}>
                            <td>
                                <div className="td-movie">
                                    <div className="movie-thumb">{emoji}</div>
                                    <div>
                                        <div className="td-title">{item.title || 'Movie #' + item.movie_id}</div>
                                        <div className="td-genre">{genres.slice(0, 2).join(' · ')}</div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                {item.rating ? (
                                    <div className="star-display">{starsHTML(item.rating)}</div>
                                ) : (
                                    <span style={{ color: 'var(--dim)', fontFamily: 'var(--ff-mono)', fontSize: '11px' }}>Not rated</span>
                                )}
                            </td>
                            <td>
                                <span className={`badge ${sentiment}`}>
                                    {sentimentLabels[sentiment]}
                                </span>
                            </td>
                            <td className="td-date">{formatDate(item.watched_at)}</td>
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
};

export default HistoryTable;
