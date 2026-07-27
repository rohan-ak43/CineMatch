import { useState, useMemo, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, X } from 'lucide-react';
import { movies } from '../data/mockData';
import { MovieCard } from '../components/movie/MovieCard';
import { EmptyState } from '../components/ui/States';

export function SearchPage() {
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') ?? '');

  useEffect(() => {
    const q = searchParams.get('q');
    if (q) setQuery(q);
  }, [searchParams]);

  const results = useMemo(() => {
    if (!query.trim()) return movies;
    const q = query.toLowerCase();
    return movies.filter(
      (m) =>
        m.title.toLowerCase().includes(q) ||
        m.genres.some((g) => g.toLowerCase().includes(q)) ||
        m.director.toLowerCase().includes(q) ||
        m.cast.some((c) => c.toLowerCase().includes(q))
    );
  }, [query]);

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      {/* Search input */}
      <div className="mb-10">
        <h1 className="font-display text-4xl font-bold text-mist-100 mb-6">Search</h1>
        <div className="flex items-center gap-3 rounded-2xl bg-void-800 px-5 py-3.5 ring-1 ring-white/10 focus-within:ring-ember-500/40 transition-all">
          <Search className="h-5 w-5 text-mist-500 shrink-0" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search movies, genres, directors, cast…"
            className="flex-1 bg-transparent text-mist-100 placeholder:text-mist-500 focus:outline-none text-base"
            autoFocus
          />
          {query && (
            <button onClick={() => setQuery('')} className="text-mist-500 hover:text-mist-200 transition-colors">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Results count */}
      {query && (
        <p className="mb-6 text-sm text-mist-500">
          {results.length > 0
            ? `${results.length} result${results.length !== 1 ? 's' : ''} for "${query}"`
            : `No results for "${query}"`}
        </p>
      )}

      {/* Results grid */}
      {results.length > 0 ? (
        <motion.div layout className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {results.map((movie, i) => (
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
      ) : (
        <EmptyState
          title="No results found"
          description={`We couldn't find anything matching "${query}". Try a different title, genre, or director.`}
          action={{ label: 'Browse All Movies', to: '/movies' }}
        />
      )}
    </div>
  );
}