import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { Play, Heart, Bookmark, Star, Clock, Calendar, Globe2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { MovieService } from '../lib/api';
import { movies, explainableFor } from '../data/mockData';
import { useAppStore } from '../store/useAppStore';
import { toast } from '../components/ui/Toast';
import { MovieCard } from '../components/movie/MovieCard';
import { formatRuntime, cn } from '../lib/utils';
import { ErrorState } from '../components/ui/States';
import { Shimmer } from '../components/ui/LoadingSkeleton';
import { Reviews } from '../components/Reviews';
import type { Movie } from '../data/mockData';

export function MovieDetails() {
    const { id } = useParams<{ id: string }>();
    const { data: movie, isLoading, isError } = useQuery({
        queryKey: ['movie', id],
        queryFn: () => MovieService.get(id!),
        enabled: !!id,
    });

    const store = useAppStore();
    const isFav = movie ? store.isFavorite(movie.id) : false;
    const { toggleFavorite, addHistory, history } = store;

    if (isLoading) {
        return (
            <div className="mx-auto max-w-5xl px-6 py-16">
                <Shimmer className="h-72 w-full" />
            </div>
        );
    }
    if (isError || !movie) {
        return <div className="mx-auto max-w-3xl px-6 py-16"><ErrorState message="That movie couldn't be found." /></div>;
    }

    const similar = movies.filter((m) => m.id !== movie.id && m.genres.some((g) => movie.genres.includes(g))).slice(0, 5);
    const watched = history.length ? history.map((h) => h.movie) : [movies[0], movies[1]];

    return (
        <div>
            <div className="relative h-[46vh] min-h-[320px] w-full overflow-hidden sm:h-[56vh]">
                <img src={movie.backdrop} alt="" className="h-full w-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-void-950 via-void-950/70 to-void-950/10" />
                <div className="absolute inset-0 bg-gradient-to-r from-void-950/70 via-transparent to-transparent" />
            </div>

            <div className="mx-auto -mt-32 max-w-6xl px-6 pb-16 sm:-mt-40">
                <div className="flex flex-col gap-6 sm:flex-row">
                    <img
                        src={movie.poster}
                        alt={`${movie.title} poster`}
                        className="w-40 shrink-0 rounded-xl shadow-2xl ring-1 ring-white/10 sm:w-56"
                    />

                    <div className="flex-1 pt-2">
                        <motion.h1
                            initial={{ opacity: 0, y: 12 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="font-display text-3xl font-extrabold text-mist-100 sm:text-4xl"
                        >
                            {movie.title}
                        </motion.h1>

                        <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-mist-300">
                            <span className="flex items-center gap-1"><Star className="h-4 w-4 fill-gilt-400 text-gilt-400" strokeWidth={0} />{movie.rating.toFixed(1)}</span>
                            <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />{movie.year}</span>
                            <span className="flex items-center gap-1"><Clock className="h-4 w-4" />{formatRuntime(movie.runtime)}</span>
                            <span className="flex items-center gap-1"><Globe2 className="h-4 w-4" />{movie.language}</span>
                        </div>

                        <div className="mt-3 flex flex-wrap gap-1.5">
                            {movie.genres.map((g) => (
                                <span key={g} className="rounded-full bg-void-800 px-2.5 py-1 text-xs text-mist-300 ring-1 ring-white/10">{g}</span>
                            ))}
                        </div>

                        <p className="mt-4 max-w-2xl text-sm leading-relaxed text-mist-300">{movie.synopsis}</p>

                        <div className="mt-6 flex flex-wrap gap-3">
                            <button
                                onClick={() => toast('Trailer would open here — hook up a real source to play it.', 'info')}
                                className="flex items-center gap-2 rounded-full bg-ember-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-ember-500/25 btn-glow"
                            >
                                <Play className="h-4 w-4" fill="currentColor" /> Watch trailer
                            </button>
                            <button
                                onClick={() => { toggleFavorite(movie); toast(isFav ? `Removed ${movie.title} from favorites` : `Added ${movie.title} to favorites`); }}
                                className={cn('flex items-center gap-2 rounded-full px-5 py-2.5 text-sm font-semibold ring-1 ring-white/10', isFav ? 'bg-ember-500/20 text-ember-400' : 'bg-void-800 text-mist-100')}
                            >
                                <Heart className="h-4 w-4" fill={isFav ? 'currentColor' : 'none'} /> {isFav ? 'In favorites' : 'Add to favorites'}
                            </button>
                            <button
                                onClick={() => { addHistory(movie); toast(`Added ${movie.title} to your watch history`, 'info'); }}
                                className="flex items-center gap-2 rounded-full bg-void-800 px-5 py-2.5 text-sm font-semibold text-mist-100 ring-1 ring-white/10"
                            >
                                <Bookmark className="h-4 w-4" /> Add to history
                            </button>
                        </div>
                    </div>
                </div>

                <div className="mt-12 grid gap-8 lg:grid-cols-3">
                    <div className="lg:col-span-2">
                        <h2 className="font-display text-lg font-bold text-mist-100">Details</h2>
                        <dl className="mt-4 grid grid-cols-2 gap-x-6 gap-y-3 text-sm sm:grid-cols-3">
                            <Detail label="Director" value={movie.director} />
                            <Detail label="Writers" value={movie.writers.join(', ')} />
                            <Detail label="Budget" value={movie.budget} />
                            <Detail label="Revenue" value={movie.revenue} />
                            <Detail label="Streaming on" value={movie.streamingOn.join(', ')} />
                            <Detail label="Cast" value={movie.cast.join(', ')} />
                        </dl>

                        <div className="mt-8 rounded-2xl border border-dusk-500/25 bg-dusk-500/5 p-4">
                            <p className="text-xs font-semibold uppercase tracking-wide text-dusk-400">Why we'd recommend this</p>
                            <p className="mt-1.5 text-sm text-mist-300">{explainableFor(movie, watched)}</p>
                        </div>
                    </div>

                    <div className="glass h-fit rounded-2xl p-4">
                        <h2 className="font-display text-sm font-bold text-mist-100">Awards & recognition</h2>
                        <p className="mt-2 text-sm text-mist-500">
                            Sourced from critic aggregates once a review API is connected — placeholder for now.
                        </p>
                    </div>
                </div>

                {similar.length > 0 && (
                    <div className="mt-14">
                        <h2 className="mb-4 font-display text-lg font-bold text-mist-100">Similar movies</h2>
                        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-5">
                            {similar.map((m) => <MovieCard key={m.id} movie={m} />)}
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