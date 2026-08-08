//Cinematch/Frontend/src/App.tsx

import { Suspense, lazy } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { ToastHost } from './components/ui/Toast';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Shimmer } from './components/ui/LoadingSkeleton';

const Home = lazy(() => import('./pages/Home').then((m) => ({ default: m.Home })));
const Movies = lazy(() => import('./pages/Movies').then((m) => ({ default: m.Movies })));
const MovieDetails = lazy(() => import('./pages/MovieDetails').then((m) => ({ default: m.MovieDetails })));
const MoodAnalysis = lazy(() => import('./pages/MoodAnalysis').then((m) => ({ default: m.MoodAnalysis })));
const RecommendationEngine = lazy(() => import('./pages/RecommendationEngine').then((m) => ({ default: m.RecommendationEngine })));
const Favorites = lazy(() => import('./pages/Favorites').then((m) => ({ default: m.Favorites })));
const SearchPage = lazy(() => import('./pages/Search').then((m) => ({ default: m.SearchPage })));
const Profile = lazy(() => import('./pages/Profile').then((m) => ({ default: m.Profile })));
const WatchHistory = lazy(() => import('./pages/WatchHistory').then((m) => ({ default: m.WatchHistory })));
const Dashboard = lazy(() => import('./pages/Dashboard').then((m) => ({ default: m.Dashboard })));
const Login = lazy(() => import('./pages/Login').then((m) => ({ default: m.Login })));
const Signup = lazy(() => import('./pages/Signup').then((m) => ({ default: m.Signup })));
const ForgotPassword = lazy(() => import('./pages/ForgotPassword').then((m) => ({ default: m.ForgotPassword })));
const NotFound = lazy(() => import('./pages/NotFound').then((m) => ({ default: m.NotFound })));

function PageFallback() {
    return (
        <div className="mx-auto max-w-7xl px-6 py-10">
            <Shimmer className="h-64 w-full" />
        </div>
    );
}

export default function App() {
    const location = useLocation();
    const isAuthRoute = ['/login', '/signup', '/forgot-password'].includes(location.pathname);

    return (
        <div className="flex min-h-screen flex-col bg-void-950">
            {!isAuthRoute && <Navbar />}
            <main className="flex-1">
                <ErrorBoundary>
                    <Suspense fallback={<PageFallback />}>
                        <AnimatePresence mode="wait">
                            <motion.div
                                key={location.pathname}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                transition={{ duration: 0.2 }}
                            >
                                <Routes location={location}>
                                    <Route path="/" element={<Home />} />
                                    <Route path="/movies" element={<Movies />} />
                                    <Route path="/movies/:id" element={<MovieDetails />} />
                                    <Route path="/mood" element={<MoodAnalysis />} />
                                    <Route path="/recommendations" element={<RecommendationEngine />} />
                                    <Route path="/favorites" element={<Favorites />} />
                                    <Route path="/search" element={<SearchPage />} />
                                    <Route path="/profile" element={<Profile />} />
                                    <Route path="/history" element={<WatchHistory />} />
                                    <Route path="/dashboard" element={<Dashboard />} />
                                    <Route path="/login" element={<Login />} />
                                    <Route path="/signup" element={<Signup />} />
                                    <Route path="/forgot-password" element={<ForgotPassword />} />
                                    <Route path="*" element={<NotFound />} />
                                </Routes>
                            </motion.div>
                        </AnimatePresence>
                    </Suspense>
                </ErrorBoundary>
            </main>
            {!isAuthRoute && <Footer />}
            <ToastHost />
        </div>
    );
}