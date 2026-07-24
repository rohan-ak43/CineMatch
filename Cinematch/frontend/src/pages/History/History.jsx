import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../../components/layout/Navbar';
import StatsCards from '../../components/history/StatsCards';
import SentimentChart from '../../components/history/SentimentChart';
import HistoryTable from '../../components/history/HistoryTable';
import api from '../../services/api';
import './History.css';

const History = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await api.get('/get_history?limit=50');
                setHistory(res.data.history || []);
            } catch (err) {
                console.error('Failed to load history', err);
                // Demo data fallback
                setHistory([
                    { movie_id: 1, title: 'Toy Story (1995)', genre: 'Adventure|Animation|Children', watched_at: '2025-04-20T14:30:00', rating: 4, sentiment: 'positive' },
                    { movie_id: 6, title: 'Heat (1995)', genre: 'Action|Crime|Thriller', watched_at: '2025-04-19T20:15:00', rating: 5, sentiment: 'positive' },
                    { movie_id: 16, title: 'Casino (1995)', genre: 'Crime|Drama', watched_at: '2025-04-18T22:00:00', rating: 3, sentiment: 'neutral' },
                    { movie_id: 17, title: 'Sense & Sensibility (1995)', genre: 'Drama|Romance', watched_at: '2025-04-15T19:45:00', rating: 4, sentiment: 'positive' },
                    { movie_id: 22, title: 'Copycat (1995)', genre: 'Crime|Drama|Thriller', watched_at: '2025-04-12T21:10:00', rating: 2, sentiment: 'negative' },
                ]);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, []);

    const sentCounts = { positive: 0, neutral: 0, negative: 0, none: 0 };
    let ratedCount = 0;
    let totalRating = 0;

    history.forEach(item => {
        const sentiment = item.sentiment || 'none';
        sentCounts[sentiment] = (sentCounts[sentiment] || 0) + 1;
        if (item.rating) {
            ratedCount++;
            totalRating += parseFloat(item.rating);
        }
    });

    const avgRating = ratedCount > 0 ? (totalRating / ratedCount).toFixed(1) : '—';
    const reviewedCount = history.filter(h => h.sentiment && h.sentiment !== 'none').length;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflowY: 'auto' }}>
            <Navbar />
            
            <div className="page-content">
                <div className="page-header">
                    <div className="page-title">My Film History</div>
                    <div className="page-sub">Your complete viewing record and sentiment analysis</div>
                </div>
                <div className="gold-line"></div>

                <StatsCards 
                    total={history.length} 
                    rated={ratedCount} 
                    avg={avgRating} 
                    reviews={reviewedCount} 
                />

                {history.length > 0 && <SentimentChart counts={sentCounts} />}

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--muted)' }}>Loading history...</div>
                ) : history.length === 0 ? (
                    <div className="empty-history">
                        <span className="empty-icon">🎞</span>
                        <div className="empty-text">Your viewing history will appear here</div>
                        <Link className="btn-go" to="/dashboard">Discover Films</Link>
                    </div>
                ) : (
                    <HistoryTable history={history} />
                )}
            </div>
        </div>
    );
};

export default History;
