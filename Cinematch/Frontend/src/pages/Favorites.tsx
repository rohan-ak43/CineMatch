import { motion } from 'framer-motion';
import { Heart } from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { MovieCard } from '../components/movie/MovieCard';
import { EmptyState } from '../components/ui/States';

export function Favorites() {
  const { favorites } = useAppStore();

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <div className="mb-8 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-ember-500/10">
          <Heart className="h-5 w-5 text-ember-400" fill="currentColor" />
        </div>
        <div>
          <h1 className="font-display text-3xl font-bold text-mist-100">My Favorites</h1>
          <p className="text-sm text-mist-500">{favorites.length} saved film{favorites.length !== 1 ? 's' : ''}</p>
        </div>
      </div>

      {favorites.length === 0 ? (
        <EmptyState
          icon={Heart}
          title="No favorites yet"
          description="Start adding films you love and they'll appear here."
          action={{ label: 'Browse Movies', to: '/movies' }}
        />
      ) : (
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
          {favorites.map((movie, i) => (
            <motion.div
              key={movie.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.07 }}
            >
              <MovieCard movie={movie} />
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}