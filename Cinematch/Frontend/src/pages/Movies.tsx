import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Filter, ChevronDown, SlidersHorizontal } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { tmdbService } from '../lib/tmdb';
import { MovieCard } from '../components/movie/MovieCard';
import { MovieGridSkeleton } from '../components/ui/LoadingSkeleton';
import { cn } from '../lib/utils';
import type { Movie } from '../data/mockData';


const SORT_OPTIONS = [
  { value: 'popularity.desc', label: 'Most Popular' },
  { value: 'vote_average.desc', label: 'Top Rated' },
  { value: 'release_date.desc', label: 'Newest First' },
  { value: 'release_date.asc', label: 'Oldest First' },
];

const GENRES = [
  { id: 0, name: 'All' },
  { id: 28, name: 'Action' },
  { id: 12, name: 'Adventure' },
  { id: 16, name: 'Animation' },
  { id: 35, name: 'Comedy' },
  { id: 80, name: 'Crime' },
  { id: 99, name: 'Documentary' },
  { id: 18, name: 'Drama' },
  { id: 10751, name: 'Family' },
  { id: 14, name: 'Fantasy' },
  { id: 27, name: 'Horror' },
  { id: 9648, name: 'Mystery' },
  { id: 10749, name: 'Romance' },
  { id: 878, name: 'Science Fiction' },
  { id: 53, name: 'Thriller' },
  { id: 37, name: 'Western' },
];

const MIN_RATING_OPTIONS = [0, 5, 6, 7, 7.5, 8, 8.5];

export function Movies() {
  const [genreId, setGenreId] = useState(0);
  const [sortBy, setSortBy] = useState('popularity.desc');
  const [minRating, setMinRating] = useState(0);
  const [page, setPage] = useState(1);
  const [allMovies, setAllMovies] = useState<Movie[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['discover', genreId, sortBy, minRating, page],
    queryFn: async () => {
      const result = await tmdbService.discover({
        page,
        genreIds: genreId > 0 ? [genreId] : undefined,
        sortBy,
        voteAverageGte: minRating > 0 ? minRating : undefined,
        voteCountGte: sortBy === 'vote_average.desc' ? 200 : 50,
      });
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
    staleTime: 5 * 60 * 1000,
  });

  const handleFilterChange = useCallback(() => {
    setPage(1);
    setAllMovies([]);
  }, []);

  const handleGenre = (id: number) => {
    setGenreId(id);
    setPage(1);
    setAllMovies([]);
  };

  const handleSort = (val: string) => {
    setSortBy(val);
    handleFilterChange();
  };

  const handleRating = (val: number) => {
    setMinRating(val);
    handleFilterChange();
  };

  const canLoadMore = data ? page < data.totalPages : false;
  const totalResults = data?.totalResults ?? 0;

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      {/* Header */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="font-display text-4xl font-bold text-mist-100">Browse Movies</h1>
          <p className="mt-1 text-mist-500">
            {isLoading ? 'Loading…' : `${totalResults.toLocaleString()} film${totalResults !== 1 ? 's' : ''} found`}
          </p>
        </div>
        <button
          onClick={() => setShowFilters(v => !v)}
          className={cn(
            'flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium ring-1 transition-all',
            showFilters
              ? 'bg-ember-500 text-white ring-ember-500'
              : 'bg-void-800 text-mist-300 ring-white/10 hover:text-mist-100'
          )}
        >
          <SlidersHorizontal className="h-4 w-4" />
          Filters
        </button>
      </div>

      {/* Expandable Filter Panel */}
      {showFilters && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 rounded-2xl border border-white/10 bg-void-800/60 p-5 backdrop-blur-sm space-y-5"
        >
          {/* Sort */}
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-mist-500 w-20">Sort by</span>
            <div className="flex flex-wrap gap-2">
              {SORT_OPTIONS.map(o => (
                <button
                  key={o.value}
                  onClick={() => handleSort(o.value)}
                  className={cn(
                    'rounded-full px-3 py-1 text-xs font-semibold transition-all',
                    sortBy === o.value
                      ? 'bg-ember-500 text-white shadow-lg shadow-ember-500/20'
                      : 'bg-void-700 text-mist-400 ring-1 ring-white/10 hover:text-mist-100'
                  )}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </div>

          {/* Min Rating */}
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs font-semibold uppercase tracking-wider text-mist-500 w-20">Min rating</span>
            <div className="flex flex-wrap gap-2">
              {MIN_RATING_OPTIONS.map(r => (
                <button
                  key={r}
                  onClick={() => handleRating(r)}
                  className={cn(
                    'rounded-full px-3 py-1 text-xs font-semibold transition-all',
                    minRating === r
                      ? 'bg-gilt-500 text-void-950 shadow-lg'
                      : 'bg-void-700 text-mist-400 ring-1 ring-white/10 hover:text-mist-100'
                  )}
                >
                  {r === 0 ? 'Any' : `${r}+`}
                </button>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Genre pills */}
      <div className="mb-8 flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-mist-500 uppercase tracking-wider mr-1">
          <Filter className="h-3.5 w-3.5" /> Genre
        </div>
        {GENRES.map(g => (
          <button
            key={g.id}
            onClick={() => handleGenre(g.id)}
            className={cn(
              'rounded-full px-3 py-1 text-xs font-semibold transition-all',
              genreId === g.id
                ? 'bg-ember-500 text-white shadow-lg shadow-ember-500/20'
                : 'bg-void-800 text-mist-400 ring-1 ring-white/10 hover:text-mist-100'
            )}
          >
            {g.name}
          </button>
        ))}
      </div>

      {/* Movie grid */}
      {isLoading && page === 1 ? (
        <MovieGridSkeleton count={20} />
      ) : (
        <>
          <motion.div layout className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
            {allMovies.map((movie, i) => (
              <motion.div
                key={movie.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: Math.min(i * 0.03, 0.5) }}
              >
                <MovieCard movie={movie} />
              </motion.div>
            ))}
          </motion.div>

          {/* Load more */}
          {canLoadMore && (
            <div className="mt-12 flex justify-center">
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={isFetching}
                className="flex items-center gap-2 rounded-full border border-white/10 bg-void-800 px-8 py-3 text-sm font-semibold text-mist-100 transition-all hover:bg-void-700 disabled:opacity-50"
              >
                {isFetching ? (
                  <span className="flex items-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-ember-500 border-t-transparent" />
                    Loading…
                  </span>
                ) : (
                  <>
                    <ChevronDown className="h-4 w-4" /> Load more movies
                  </>
                )}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}