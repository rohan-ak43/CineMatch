import { motion } from 'framer-motion';
import { BarChart2, Heart, Clock, Star, TrendingUp, Film } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAppStore } from '../store/useAppStore';
import { tmdbService } from '../lib/tmdb';

function StatCard({ icon: Icon, label, value, color }: { icon: React.ElementType; label: string; value: string | number; color: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass rounded-2xl p-5"
    >
      <Icon className={`mb-3 h-8 w-8 ${color}`} />
      <p className="text-2xl font-bold font-display text-mist-100">{value}</p>
      <p className="mt-0.5 text-sm text-mist-500">{label}</p>
    </motion.div>
  );
}

export function Dashboard() {
  const { favorites, history } = useAppStore();

  const { data: popularData } = useQuery({
    queryKey: ['popular', 1],
    queryFn: () => tmdbService.getPopular(1),
    staleTime: 10 * 60 * 1000,
  });

  const topGenre = (() => {
    const counts: Record<string, number> = {};
    [...favorites, ...history.map(h => h.movie)].forEach(m => {
      m.genres.forEach(g => { counts[g] = (counts[g] || 0) + 1; });
    });
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    return sorted[0]?.[0] ?? '—';
  })();

  const avgRating = favorites.length
    ? (favorites.reduce((s, m) => s + m.rating, 0) / favorites.length).toFixed(1)
    : '—';

  const recentMovies = history.slice(0, 4).map(h => h.movie);

  // "Suggested for you" — popular movies not already in favorites
  const favoriteIds = new Set(favorites.map(f => f.id));
  const suggestedMovies = (popularData?.movies ?? [])
    .filter(m => !favoriteIds.has(m.id))
    .slice(0, 3);

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-dusk-500/10">
            <BarChart2 className="h-5 w-5 text-dusk-400" />
          </div>
          <h1 className="font-display text-3xl font-bold text-mist-100">Dashboard</h1>
        </div>
        <p className="text-mist-500 text-sm">Your personal movie stats at a glance.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4 mb-10">
        <StatCard icon={Clock} label="Movies Watched" value={history.length} color="text-dusk-400" />
        <StatCard icon={Heart} label="Favorites" value={favorites.length} color="text-ember-400" />
        <StatCard icon={Film} label="Top Genre" value={topGenre} color="text-gilt-400" />
        <StatCard icon={Star} label="Avg. Rating Saved" value={avgRating} color="text-emerald-400" />
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        {/* Recent activity */}
        <div className="lg:col-span-2 glass rounded-2xl p-6">
          <h2 className="font-display text-lg font-bold text-mist-100 mb-4 flex items-center gap-2">
            <Clock className="h-4 w-4 text-dusk-400" /> Recent Watches
          </h2>

          {recentMovies.length === 0 ? (
            <p className="text-sm text-mist-500 py-4">
              No watch history yet. <Link to="/movies" className="text-ember-400 hover:underline">Browse movies</Link>
            </p>
          ) : (
            <div className="flex flex-col gap-3">
              {recentMovies.map(movie => (
                <Link
                  key={movie.id}
                  to={`/movies/${movie.id}`}
                  className="flex items-center gap-3 rounded-xl bg-void-800/40 p-3 hover:bg-void-800/80 transition-colors"
                >
                  <img src={movie.poster} alt="" className="h-12 w-8 rounded-lg object-cover" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-mist-100 truncate">{movie.title}</p>
                    <p className="text-xs text-mist-500">{movie.genres[0]} · {movie.year}</p>
                  </div>
                  <div className="flex items-center gap-1 shrink-0">
                    <Star className="h-3 w-3 fill-gilt-400 text-gilt-400" strokeWidth={0} />
                    <span className="text-xs text-gilt-400">{movie.rating.toFixed(1)}</span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Suggested */}
        <div className="glass rounded-2xl p-6">
          <h2 className="font-display text-lg font-bold text-mist-100 mb-4 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-ember-400" /> Suggested For You
          </h2>
          <div className="flex flex-col gap-3">
            {suggestedMovies.map(movie => (
              <Link
                key={movie.id}
                to={`/movies/${movie.id}`}
                className="flex items-center gap-3 rounded-xl bg-void-800/40 p-2.5 hover:bg-void-800/80 transition-colors"
              >
                <img src={movie.poster} alt="" className="h-12 w-8 rounded-lg object-cover" />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-semibold text-mist-100 truncate">{movie.title}</p>
                  <p className="text-xs text-mist-500">{movie.genres[0]}</p>
                </div>
              </Link>
            ))}
          </div>
          <Link to="/recommendations" className="mt-4 block text-center text-xs font-medium text-ember-400 hover:text-ember-300">
            View all recommendations →
          </Link>
        </div>
      </div>
    </div>
  );
}