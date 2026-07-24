import React, { useState, useEffect } from 'react';
import Navbar from '../../components/layout/Navbar';
import Sidebar from '../../components/layout/Sidebar';
import MovieCard from '../../components/movies/MovieCard';
import LoadingSkeleton from '../../components/movies/LoadingSkeleton';
import ReviewModal from '../../components/shared/ReviewModal';
import api from '../../services/api';
import './Dashboard.css';

const Dashboard = () => {
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedMovie, setSelectedMovie] = useState(null);
    const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
    const [isSavingReview, setIsSavingReview] = useState(false);

    useEffect(() => {
        loadRecommendations({});
    }, []);

    const loadRecommendations = async (filters) => {
        setLoading(true);
        try {
            const query = new URLSearchParams(filters).toString();
            const res = await api.get(`/recommend?${query}`);
            setMovies(res.data.recommendations || []);
        } catch (err) {
            console.error('Failed to load recommendations', err);
            // Demo data fallback
            setTimeout(() => {
                setMovies([
                    { movie_id: 1, title: 'Toy Story (1995)', genre: 'Adventure|Animation|Children', rating: 4, review_text: 'A masterpiece.', sentiment: 'positive', predicted_score: 98 },
                    { movie_id: 2, title: 'Jumanji (1995)', genre: 'Adventure|Children|Fantasy', rating: 0, predicted_score: 85 },
                    { movie_id: 3, title: 'Grumpier Old Men (1995)', genre: 'Comedy|Romance', rating: 3, review_text: 'It was okay.', sentiment: 'neutral', predicted_score: 72 },
                    { movie_id: 10, title: 'GoldenEye (1995)', genre: 'Action|Adventure|Thriller', rating: 5, predicted_score: 95 },
                    { movie_id: 14, title: 'Nixon (1995)', genre: 'Drama', rating: 2, review_text: 'Too long and boring.', sentiment: 'negative', predicted_score: 40 },
                ]);
                setLoading(false);
            }, 800);
            return;
        }
        setLoading(false);
    };

    const handleRate = async (movieId, rating) => {
        // Optimistic update
        setMovies(prev => prev.map(m => m.movie_id === movieId ? { ...m, rating } : m));
        try {
            await api.post('/rate', { movie_id: movieId, rating });
        } catch (err) {
            console.error('Failed to rate movie', err);
        }
    };

    const handleReviewClick = (movie) => {
        setSelectedMovie(movie);
        setIsReviewModalOpen(true);
    };

    const handleSaveReview = async (text) => {
        if (!selectedMovie) return;
        setIsSavingReview(true);
        try {
            const res = await api.post('/review', { movie_id: selectedMovie.movie_id, review_text: text });
            // Update local state with new review text and sentiment
            setMovies(prev => prev.map(m => 
                m.movie_id === selectedMovie.movie_id 
                ? { ...m, review_text: text, sentiment: res.data.sentiment } 
                : m
            ));
        } catch (err) {
            console.error('Failed to save review', err);
            // Demo fallback
            setTimeout(() => {
                setMovies(prev => prev.map(m => 
                    m.movie_id === selectedMovie.movie_id 
                    ? { ...m, review_text: text, sentiment: 'positive' } 
                    : m
                ));
                setIsSavingReview(false);
                setIsReviewModalOpen(false);
                setSelectedMovie(null);
            }, 500);
            return;
        }
        
        setIsSavingReview(false);
        setIsReviewModalOpen(false);
        setSelectedMovie(null);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            <Navbar />
            <div className="main">
                <Sidebar onRecommend={loadRecommendations} loading={loading} />
                
                <main className="content">
                    <div className="section-header">
                        <h1 className="section-title">Recommended for You</h1>
                        <span className="section-count">{movies.length} FILMS</span>
                    </div>

                    <div className="movie-grid">
                        {loading && <LoadingSkeleton count={10} />}
                        
                        {!loading && movies.length === 0 && (
                            <div className="empty-state">
                                <span className="empty-state-icon">🍿</span>
                                <div className="empty-state-text">No recommendations found. Adjust your filters and try again.</div>
                            </div>
                        )}

                        {!loading && movies.map(movie => (
                            <MovieCard 
                                key={movie.movie_id} 
                                movie={movie} 
                                onRate={handleRate} 
                                onReview={handleReviewClick} 
                            />
                        ))}
                    </div>
                </main>
            </div>

            <ReviewModal 
                isOpen={isReviewModalOpen} 
                onClose={() => setIsReviewModalOpen(false)}
                movie={selectedMovie}
                onSave={handleSaveReview}
                isSaving={isSavingReview}
            />
        </div>
    );
};

export default Dashboard;
