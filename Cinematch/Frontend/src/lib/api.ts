// Re-export everything from the TMDB service for backward compatibility.
// Any file that imports { MovieService } from '../lib/api' will automatically
// use the live TMDB implementation.
export { MovieService, tmdbService, posterUrl, backdropUrl, MOOD_GENRE_MAP } from './tmdb';
export type { MovieListResult, DiscoverParams } from './tmdb';
export type { Movie } from '../data/mockData';
