import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Filter } from 'lucide-react';
import { movies } from '../data/mockData';
import { MovieCard } from '../components/movie/MovieCard';
import { cn } from '../lib/utils';

const allGenres = ['All', ...Array.from(new Set(movies.flatMap((m) => m.genres))).sort()];

const sortOptions = [
  { value: 'rating', label: 'Top Rated' },
  { value: 'year', label: 'Newest' },
  { value: 'title', label: 'A–Z' },
];

export function Movies() {
  const [genre, setGenre] = useState('All');
  const [sort, setSort] = useState('rating');

  const filtered = useMemo(() => {
    let result = genre === 'All' ? [...movies] : movies.filter((m) => m.genres.includes(genre));
    if (sort === 'rating') result.sort((a, b) => b.rating - a.rating);
    else if (sort === 'year') result.sort((a, b) => b.year - a.year);
    else result.sort((a, b) => a.title.localeCompare(b.title));
    return result;
  }, [genre, sort]);

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-display text-4xl font-bold text-mist-100">Browse Movies</h1>
        <p className="mt-1 text-mist-500">{filtered.length} film{filtered.length !== 1 ? 's' : ''} available</p>
      </div>

      {/* Filters */}
      <div className="mb-8 flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-mist-500 uppercase tracking-wider">
          <Filter className="h-3.5 w-3.5" /> Genre
        </div>
        <div className="flex flex-wrap gap-2">
          {allGenres.map((g) => (
            <button
              key={g}
              onClick={() => setGenre(g)}
              className={cn(
                'rounded-full px-3 py-1 text-xs font-semibold transition-all',
                genre === g
                  ? 'bg-ember-500 text-white shadow-lg shadow-ember-500/20'
                  : 'bg-void-800 text-mist-400 ring-1 ring-white/10 hover:text-mist-100'
              )}
            >
              {g}
            </button>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-mist-500">Sort:</span>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="rounded-lg bg-void-800 px-3 py-1.5 text-xs text-mist-100 ring-1 ring-white/10 focus:outline-none focus:ring-ember-500/50"
          >
            {sortOptions.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Grid */}
      <motion.div
        layout
        className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5"
      >
        {filtered.map((movie, i) => (
          <motion.div
            key={movie.id}
            layout
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
          >
            <MovieCard movie={movie} />
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}