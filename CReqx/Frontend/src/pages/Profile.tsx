import { motion } from 'framer-motion';
import { User, Heart, Clock, Star, Settings, Camera } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';

const GENRES = ['Action', 'Sci-Fi', 'Drama', 'Thriller', 'Comedy', 'Romance', 'Animation', 'Horror'];

export function Profile() {
  const { favorites, history } = useAppStore();

  const topGenres = (() => {
    const counts: Record<string, number> = {};
    [...favorites, ...history.map((h) => h.movie)].forEach((m) => {
      m.genres.forEach((g) => { counts[g] = (counts[g] || 0) + 1; });
    });
    return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 3).map(([g]) => g);
  })();

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      {/* Profile Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass mb-8 rounded-3xl p-8"
      >
        <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
          {/* Avatar */}
          <div className="relative">
            <div className="flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-ember-500 to-dusk-500 text-3xl font-bold text-white ring-4 ring-void-800">
              R
            </div>
            <button className="absolute -bottom-1 -right-1 flex h-8 w-8 items-center justify-center rounded-full bg-void-700 ring-2 ring-void-900 hover:bg-void-600 transition-colors">
              <Camera className="h-4 w-4 text-mist-300" />
            </button>
          </div>

          <div className="flex-1 text-center sm:text-left">
            <h1 className="font-display text-2xl font-bold text-mist-100">Rohan</h1>
            <p className="text-sm text-mist-500">rohan@email.com</p>
            <p className="mt-2 text-sm text-mist-400">Movie enthusiast · Member since 2024</p>
            <div className="mt-4 flex flex-wrap justify-center gap-4 sm:justify-start">
              <div className="text-center">
                <p className="text-xl font-bold font-display text-mist-100">{history.length}</p>
                <p className="text-xs text-mist-500">Watched</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-bold font-display text-mist-100">{favorites.length}</p>
                <p className="text-xs text-mist-500">Favorites</p>
              </div>
              <div className="text-center">
                <p className="text-xl font-bold font-display text-mist-100">{topGenres[0] ?? '—'}</p>
                <p className="text-xs text-mist-500">Top Genre</p>
              </div>
            </div>
          </div>

          <button className="flex items-center gap-2 rounded-full bg-void-700 px-4 py-2 text-sm font-medium text-mist-300 ring-1 ring-white/10 hover:bg-void-600 transition-all">
            <Settings className="h-4 w-4" /> Edit Profile
          </button>
        </div>
      </motion.div>

      {/* Genre Preferences */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass mb-6 rounded-2xl p-6"
      >
        <h2 className="font-display text-lg font-bold text-mist-100 mb-4">Genre Preferences</h2>
        <div className="flex flex-wrap gap-2">
          {GENRES.map((g) => {
            const isTop = topGenres.includes(g);
            return (
              <span
                key={g}
                className={`rounded-full px-3 py-1.5 text-xs font-semibold transition-all ${
                  isTop
                    ? 'bg-ember-500 text-white shadow-lg shadow-ember-500/20'
                    : 'bg-void-800 text-mist-400 ring-1 ring-white/10'
                }`}
              >
                {g} {isTop && '★'}
              </span>
            );
          })}
        </div>
        {topGenres.length === 0 && (
          <p className="mt-2 text-xs text-mist-500">
            Watch and favourite movies to discover your top genres.
          </p>
        )}
      </motion.div>

      {/* Quick Links */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-2 gap-4 sm:grid-cols-3"
      >
        {[
          { icon: Heart, label: 'My Favorites', count: favorites.length, to: '/favorites', color: 'text-ember-400' },
          { icon: Clock, label: 'Watch History', count: history.length, to: '/history', color: 'text-dusk-400' },
          { icon: Star, label: 'Dashboard', count: null, to: '/dashboard', color: 'text-gilt-400' },
        ].map((item) => (
          <Link
            key={item.to}
            to={item.to}
            className="glass flex flex-col gap-2 rounded-2xl p-5 hover:ring-1 hover:ring-white/10 transition-all card-lift"
          >
            <item.icon className={`mb-2 h-8 w-8 ${item.color}`} />
            <p className="font-display font-semibold text-mist-100">{item.label}</p>
            {item.count !== null && (
              <p className="text-sm text-mist-500">{item.count} items</p>
            )}
          </Link>
        ))}
      </motion.div>
    </div>
  );
}