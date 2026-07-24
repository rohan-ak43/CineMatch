import React, { useState } from 'react';
import api from '../../services/api';

const Sidebar = ({ onRecommend, loading }) => {
    const [mood, setMood] = useState('');
    const [moodResult, setMoodResult] = useState(null);
    const [detecting, setDetecting] = useState(false);
    
    // Filters
    const [genre, setGenre] = useState('');
    const [language, setLanguage] = useState('');
    const [year, setYear] = useState('');

    const handleDetectMood = async () => {
        if (!mood.trim()) return;
        setDetecting(true);
        setMoodResult(null);
        try {
            const res = await api.post('/detect_mood', { text: mood });
            setMoodResult(res.data);
            if (res.data.recommended_genres && res.data.recommended_genres.length > 0) {
                setGenre(res.data.recommended_genres[0]);
            }
        } catch (err) {
            console.error('Mood detection failed', err);
            // Fallback for demo
            setMoodResult({
                emoji: '✨',
                primary_emotion: 'Joy',
                recommended_genres: ['Comedy', 'Animation']
            });
            setGenre('Comedy');
        } finally {
            setDetecting(false);
        }
    };

    const handleRecommend = () => {
        onRecommend({ genre, language, year, mood });
    };

    return (
        <aside className="sidebar">
            <div>
                <div className="sidebar-section-title">How are you feeling?</div>
                <div className="mood-box">
                    <textarea 
                        className="mood-textarea" 
                        placeholder="I'm in the mood for something light and funny..."
                        value={mood}
                        onChange={e => setMood(e.target.value)}
                    />
                    <button className="mood-detect-btn" onClick={handleDetectMood} disabled={detecting}>
                        {detecting ? 'Analyzing...' : 'Detect Mood'}
                    </button>
                </div>
                {moodResult && (
                    <div className="mood-result show">
                        <div className="mood-emoji">{moodResult.emoji || '✨'}</div>
                        <div className="mood-info">
                            <span className="mood-label">{moodResult.primary_emotion}</span>
                            <div className="mood-genres">Matches: {(moodResult.recommended_genres || []).join(', ')}</div>
                        </div>
                    </div>
                )}
            </div>

            <div>
                <div className="sidebar-section-title">Manual Filters</div>
                <div className="filter-row">
                    <div>
                        <label className="filter-label">Genre</label>
                        <select className="filter-select" value={genre} onChange={e => setGenre(e.target.value)}>
                            <option value="">Any Genre</option>
                            <option value="Action">Action</option>
                            <option value="Adventure">Adventure</option>
                            <option value="Animation">Animation</option>
                            <option value="Comedy">Comedy</option>
                            <option value="Crime">Crime</option>
                            <option value="Drama">Drama</option>
                            <option value="Horror">Horror</option>
                            <option value="Romance">Romance</option>
                            <option value="Sci-Fi">Sci-Fi</option>
                            <option value="Thriller">Thriller</option>
                        </select>
                    </div>
                    <div>
                        <label className="filter-label">Language</label>
                        <select className="filter-select" value={language} onChange={e => setLanguage(e.target.value)}>
                            <option value="">Any Language</option>
                            <option value="en">English</option>
                            <option value="hi">Hindi</option>
                            <option value="ko">Korean</option>
                            <option value="ja">Japanese</option>
                            <option value="es">Spanish</option>
                        </select>
                    </div>
                    <div>
                        <label className="filter-label">Release Year</label>
                        <select className="filter-select" value={year} onChange={e => setYear(e.target.value)}>
                            <option value="">Any Time</option>
                            <option value="2020s">2020 - Present</option>
                            <option value="2010s">2010 - 2019</option>
                            <option value="2000s">2000 - 2009</option>
                            <option value="90s">1990 - 1999</option>
                            <option value="classic">Before 1990</option>
                        </select>
                    </div>
                </div>
            </div>

            <button 
                className="btn-recommend" 
                onClick={handleRecommend}
                disabled={loading}
            >
                {loading ? 'Finding...' : 'Recommend'}
            </button>
        </aside>
    );
};

export default Sidebar;
