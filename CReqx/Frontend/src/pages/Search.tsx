import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, X, ChevronDown } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { tmdbService } from '../lib/tmdb';
import { MovieCard } from '../components/movie/MovieCard';
import { MovieGridSkeleton } from '../components/ui/LoadingSkeleton';
import { EmptyState } from '../components/ui/States';
import type { Movie } from '../data/mockData';

function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export function SearchPage() {
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get('q') ?? '');
  const [page, setPage] = useState(1);
  const [allMovies, setAllMovies] = useState<Movie[]>([]);
  const debouncedQuery = useDebounce(query, 350);

  // Reset when query changes
  useEffect(() => {
    setPage(1);
    setAllMovies([]);
  }, [debouncedQuery]);

  // Sync URL param
  useEffect(() => {
    const q = searchParams.get('q');
    if (q && q !== query) setQuery(q);
  }, [searchParams]);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['search', debouncedQuery, page],
    queryFn: async () => {
      if (!debouncedQuery.trim()) return { movies: [], totalPages: 0, totalResults: 0 };
      const result = await tmdbService.search(debouncedQuery, page);
      if (page === 1) {
        setAllMovies(result.movies);
      } else {
        setAllMovies(prev => {
          const ids = new Set(prev.map(m => m.id));
          return [...prev, ...result.movies.filter(m => !ids.has(m.id))];
        });
      }
      return result;
    },
    enabled: true,
    staleTime: 2 * 60 * 1000,
  });

  const handleClear = useCallback(() => {
    setQuery('');
    setPage(1);
    setAllMovies([]);
  }, []);

  const totalResults = data?.totalResults ?? 0;
  const canLoadMore = (data?.totalPages ?? 0) > page;
  const showSkeleton = isLoading && page === 1 && !!debouncedQuery;

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      {/* Search input */}
      <div className="mb-10">
        <h1 className="font-display text-4xl font-bold text-mist-100 mb-6">Search</h1>
        <div className="flex items-center gap-3 rounded-2xl bg-void-800 px-5 py-3.5 ring-1 ring-white/10 focus-within:ring-ember-500/40 transition-all">
          <Search className="h-5 w-5 text-mist-500 shrink-0" />
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search movies, genres, directors…"
            className="flex-1 bg-transparent text-mist-100 placeholder:text-mist-500 focus:outline-none text-base"
            autoFocus
          />
          {isFetching && (
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-ember-500 border-t-transparent shrink-0" />
          )}
          {query && !isFetching && (
            <button onClick={handleClear} className="text-mist-500 hover:text-mist-200 transition-colors">
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Results meta */}
      {debouncedQuery && !showSkeleton && (
        <p className="mb-6 text-sm text-mist-500">
          {totalResults > 0
            ? `${totalResults.toLocaleString()} result${totalResults !== 1 ? 's' : ''} for "${debouncedQuery}"`
            : `No results for "${debouncedQuery}"`}
        </p>
      )}

      {/* Results */}
      {showSkeleton ? (
        <MovieGridSkeleton count={10} />
      ) : allMovies.length > 0 ? (
        <>
          <motion.div layout className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {allMovies.map((movie, i) => (
              <motion.div
                key={movie.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: Math.min(i * 0.03, 0.4) }}
              >
                <MovieCard movie={movie} />
              </motion.div>
            ))}
          </motion.div>

          {canLoadMore && (
            <div className="mt-10 flex justify-center">
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={isFetching}
                className="flex items-center gap-2 rounded-full border border-white/10 bg-void-800 px-8 py-3 text-sm font-semibold text-mist-100 transition-all hover:bg-void-700 disabled:opacity-50"
              >
                {isFetching
                  ? <><span className="h-4 w-4 animate-spin rounded-full border-2 border-ember-500 border-t-transparent" /> Loading…</>
                  : <><ChevronDown className="h-4 w-4" /> Load more results</>
                }
              </button>
            </div>
          )}
        </>
      ) : debouncedQuery ? (
        <EmptyState
          title="No results found"
          description={`We couldn't find anything matching "${debouncedQuery}". Try a different title, genre, or director.`}
          action={{ label: 'Browse All Movies', to: '/movies' }}
        />
      ) : null}
    </div>
  );
}