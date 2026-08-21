import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { Play, Heart, Bookmark, Star, Clock, Calendar, Globe2, Users, DollarSign } from 'lucide-react';
import { motion } from 'framer-motion';
import { tmdbService } from '../lib/tmdb';
import { useAppStore } from '../store/useAppStore';
import { toast } from '../components/ui/Toast';
import { MovieCard } from '../components/movie/MovieCard';
import { formatRuntime, cn } from '../lib/utils';
import { ErrorState } from '../components/ui/States';
import { Shimmer } from '../components/ui/LoadingSkeleton';
import { Reviews } from '../components/Reviews';
import { explainableFor } from '../data/mockData';

export function MovieDetails() {
    const { id } = useParams<{ id: string }>();

    const { data, isLoading, isError } = useQuery({
        queryKey: ['movie-detail', id],
        queryFn: () => tmdbService.getMovieDetail(id!),
        enabled: !!id,
        staleTime: 10 * 60 * 1000,
    });

    const store = useAppStore();
    const movie = data?.movie;
    const similar = data?.similar ?? [];
    const isFav = movie ? store.isFavorite(movie.id) : false;
    const { toggleFavorite, addHistory, history } = store;

    if (isLoading) {
        return (
            <div className="mx-auto max-w-5xl px-6 py-16 space-y-4">
                <Shimmer className="h-72 w-full rounded-2xl" />
                <div className="flex gap-6 mt-4">
                    <Shimmer className="h-64 w-44 rounded-xl shrink-0" />
                    <div className="flex-1 space-y-3">
                        <Shimmer className="h-8 w-3/4 rounded" />
                        <Shimmer className="h-4 w-1/2 rounded" />
                        <Shimmer className="h-4 w-full rounded" />
                        <Shimmer className="h-4 w-full rounded" />
                        <Shimmer className="h-4 w-2/3 rounded" />
                    </div>
                </div>
            </div>
        );
    }
    if (isError || !movie) {
        return <div className="mx-auto max-w-3xl px-6 py-16"><ErrorState message="That movie couldn't be found." /></div>;
    }

    const watched = history.length ? history.map(h => h.movie) : [];

    return (
        <div>
            {/* Backdrop */}
            <div className="relative h-[46vh] min-h-[320px] w-full overflow-hidden bg-void-900 sm:h-[56vh]">
                {movie.backdrop ? (
                    <img
                        src={movie.backdrop}
                        alt=""
                        className="h-full w-full object-cover"
                        onError={(e) => { e.currentTarget.style.display = 'none'; }}
                    />
                ) : null}
                <div className="absolute inset-0 bg-gradient-to-t from-void-950 via-void-950/70 to-void-950/10" />
                <div className="absolute inset-0 bg-gradient-to-r from-void-950/70 via-transparent to-transparent" />
            </div>

            <div className="relative z-10 mx-auto -mt-32 max-w-6xl px-6 pb-16 sm:-mt-40">
                <div className="flex flex-col gap-6 sm:flex-row">
                    {/* Poster */}
                    <img
                        src={movie.poster}
                        alt={`${movie.title} poster`}
                        className="w-40 shrink-0 rounded-xl shadow-2xl ring-1 ring-white/10 sm:w-56"
                        onError={(e) => { e.currentTarget.style.display = 'none'; }}
                    />

                    <div className="flex-1 pt-2">
                        <motion.h1
                            initial={{ opacity: 0, y: 12 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="font-display text-3xl font-extrabold text-mist-100 sm:text-4xl"
                        >
                            {movie.title}
                        </motion.h1>

                        {movie.tagline && (
                            <p className="mt-1 text-sm italic text-mist-500">{movie.tagline}</p>
                        )}

                        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-mist-300">
                            <span className="flex items-center gap-1">
                                <Star className="h-4 w-4 fill-gilt-400 text-gilt-400" strokeWidth={0} />
                                {movie.rating.toFixed(1)}
                                <span className="text-mist-500 text-xs">({movie.voteCount.toLocaleString()} votes)</span>
                            </span>
                            <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />{movie.releaseDate}</span>
                            {movie.runtime > 0 && (
                                <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{formatRuntime(movie.runtime)}</span>
                            )}
                            <span className="flex items-center gap-1"><Globe2 className="h-4 w-4" />{movie.language}</span>
                        </div>

                        {/* Genre badges */}
                        <div className="mt-3 flex flex-wrap gap-1.5">
                            {movie.genres.map(g => (
                                <span key={g} className="rounded-full bg-void-800 px-2.5 py-1 text-xs text-mist-300 ring-1 ring-white/10">
                                    {g}
                                </span>
                            ))}
                        </div>

                        <p className="mt-4 max-w-2xl text-sm leading-relaxed text-mist-300">{movie.synopsis}</p>

                        {/* Action buttons */}
                        <div className="mt-6 flex flex-wrap gap-3">
                            {movie.trailerKey ? (
                                <a
                                    href={`https://www.youtube.com/watch?v=${movie.trailerKey}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 rounded-full bg-ember-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-ember-500/25 btn-glow transition-all hover:bg-ember-400"
                                >
                                    <Play className="h-4 w-4" fill="currentColor" /> Watch trailer
                                </a>
                            ) : (
                                <button
                                    onClick={() => toast('No trailer available for this movie.', 'info')}
                                    className="flex items-center gap-2 rounded-full bg-void-700 px-5 py-2.5 text-sm font-semibold text-mist-400 ring-1 ring-white/10"
                                >
                                    <Play className="h-4 w-4" /> Watch trailer
                                </button>
                            )}
                            <button
                                onClick={() => { toggleFavorite(movie); toast(isFav ? `Removed from favorites` : `Added to favorites`); }}
                                className={cn('flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-semibold ring-1 ring-white/10', isFav ? 'bg-ember-500/20 text-ember-400' : 'bg-void-800 text-mist-100')}
                            >
                                <Heart className="h-4 w-4" fill={isFav ? 'currentColor' : 'none'} />
                                {isFav ? 'In favorites' : 'Add to favorites'}
                            </button>
                            <button
                                onClick={() => { addHistory(movie); toast(`Added ${movie.title} to watch history`, 'info'); }}
                                className="flex items-center gap-2 rounded-full bg-void-800 px-5 py-2.5 text-sm font-semibold text-mist-100 ring-1 ring-white/10"
                            >
                                <Bookmark className="h-4 w-4" /> Add to history
                            </button>
                        </div>
                    </div>
                </div>

                {/* Trailer embed */}
                {movie.trailerKey && (
                    <div className="mt-12">
                        <h2 className="mb-4 font-display text-lg font-bold text-mist-100">Trailer</h2>
                        <div className="aspect-video w-full overflow-hidden rounded-2xl shadow-2xl">
                            <iframe
                                src={`https://www.youtube.com/embed/${movie.trailerKey}`}
                                title={`${movie.title} trailer`}
                                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                allowFullScreen
                                className="h-full w-full"
                            />
                        </div>
                    </div>
                )}

                {/* Details grid */}
                <div className="mt-12 grid gap-8 lg:grid-cols-3">
                    <div className="lg:col-span-2 space-y-8">
                        {/* Crew / details */}
                        <div>
                            <h2 className="font-display text-lg font-bold text-mist-100">Details</h2>
                            <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-3 text-sm sm:grid-cols-3">
                                {movie.director && <Detail label="Director" value={movie.director} />}
                                {movie.writers.length > 0 && <Detail label="Writers" value={movie.writers.join(', ')} />}
                                {movie.budget && movie.budget !== 'N/A' && <Detail label="Budget" value={movie.budget} />}
                                {movie.revenue && movie.revenue !== 'N/A' && <Detail label="Revenue" value={movie.revenue} />}
                                {movie.status && <Detail label="Status" value={movie.status} />}
                                {movie.originalLanguage && <Detail label="Language" value={movie.originalLanguage.toUpperCase()} />}
                            </dl>
                        </div>

                        {/* Cast */}
                        {movie.cast.length > 0 && (
                            <div>
                                <h2 className="font-display text-lg font-bold text-mist-100 flex items-center gap-2">
                                    <Users className="h-4 w-4 text-mist-400" /> Cast
                                </h2>
                                <div className="mt-3 flex flex-wrap gap-2">
                                    {movie.cast.map(name => (
                                        <span key={name} className="rounded-full bg-void-800 px-3 py-1 text-xs text-mist-300 ring-1 ring-white/10">
                                            {name}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Recommendation reason */}
                        {watched.length > 0 && (
                            <div className="rounded-2xl border border-dusk-500/25 bg-dusk-500/5 p-4">
                                <p className="text-xs font-semibold uppercase tracking-wide text-dusk-400">Why we'd recommend this</p>
                                <p className="mt-1.5 text-sm text-mist-300">{explainableFor(movie, watched)}</p>
                            </div>
                        )}
                    </div>

                    {/* Stats sidebar */}
                    <div className="glass h-fit rounded-2xl p-5 space-y-4">
                        <h2 className="font-display text-sm font-bold text-mist-100">At a glance</h2>
                        <StatRow icon={Star} label="TMDB Rating" value={`${movie.rating} / 10`} />
                        <StatRow icon={Users} label="Votes" value={movie.voteCount.toLocaleString()} />
                        {movie.runtime > 0 && <StatRow icon={Clock} label="Runtime" value={formatRuntime(movie.runtime)} />}
                        {movie.budget && movie.budget !== 'N/A' && <StatRow icon={DollarSign} label="Budget" value={movie.budget} />}
                        {movie.revenue && movie.revenue !== 'N/A' && <StatRow icon={DollarSign} label="Revenue" value={movie.revenue} />}
                    </div>
                </div>

                {/* Similar movies */}
                {similar.length > 0 && (
                    <div className="mt-14">
                        <h2 className="mb-4 font-display text-lg font-bold text-mist-100">Similar movies</h2>
                        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
                            {similar.map(m => <MovieCard key={m.id} movie={m} />)}
                        </div>
                    </div>
                )}

                <Reviews movieId={movie.id} />
            </div>
        </div>
    );
}

function Detail({ label, value }: { label: string; value: string }) {
    return (
        <div>
            <dt className="text-xs uppercase tracking-wide text-mist-500">{label}</dt>
            <dd className="mt-0.5 text-mist-200">{value}</dd>
        </div>
    );
}

function StatRow({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
    return (
        <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-1.5 text-mist-500"><Icon className="h-3.5 w-3.5" />{label}</span>
            <span className="font-semibold text-mist-100">{value}</span>
        </div>
    );
}