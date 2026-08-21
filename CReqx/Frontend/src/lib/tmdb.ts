/**
 * TMDB Service — all API calls, caching, and conversion to the app Movie type.
 * Docs: https://developer.themoviedb.org/docs
 */
import type {
  TMDBListMovie,
  TMDBMovieAppended,
  TMDBPaginatedResponse,
  TMDBGenre,
  DiscoverParams,
} from './tmdb.types';
export type { DiscoverParams } from './tmdb.types';
import type { Movie } from '../data/mockData';

// ─── Config ────────────────────────────────────────────────────────────────────
const BASE_URL = 'https://api.themoviedb.org/3';
const IMAGE_BASE = 'https://image.tmdb.org/t/p';
const API_KEY = (import.meta as ImportMeta & { env: Record<string, string> }).env?.VITE_TMDB_API_KEY ?? '';

// ─── Simple in-memory cache with 5-min TTL ─────────────────────────────────────
const _cache = new Map<string, { data: unknown; ts: number }>();
const CACHE_TTL = 5 * 60 * 1000;

function getCached<T>(key: string): T | null {
  const entry = _cache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.ts > CACHE_TTL) { _cache.delete(key); return null; }
  return entry.data as T;
}
function setCached<T>(key: string, data: T): T {
  _cache.set(key, { data, ts: Date.now() });
  return data;
}

// ─── URL builder ───────────────────────────────────────────────────────────────
function buildUrl(path: string, params: Record<string, string | number | undefined | null> = {}): string {
  const url = new URL(`${BASE_URL}${path}`);
  url.searchParams.set('api_key', API_KEY);
  url.searchParams.set('language', 'en-US');
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== '') {
      url.searchParams.set(k, String(v));
    }
  }
  return url.toString();
}

// ─── Core fetch with caching ───────────────────────────────────────────────────
async function tmdbFetch<T>(path: string, params: Record<string, string | number | undefined | null> = {}): Promise<T> {
  if (!API_KEY) {
    throw new Error('TMDB API key is missing. Create a .env file with VITE_TMDB_API_KEY=your_key');
  }
  const url = buildUrl(path, params);
  const cached = getCached<T>(url);
  if (cached) return cached;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`TMDB ${res.status}: ${res.statusText} — ${path}`);
  const data = (await res.json()) as T;
  return setCached(url, data);
}

// ─── Genre map (ID → name) ─────────────────────────────────────────────────────
// Hardcoded for instant use; also refreshed from API on first genre fetch.
export const GENRE_MAP_STATIC: Record<number, string> = {
  28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime',
  99: 'Documentary', 18: 'Drama', 10751: 'Family', 14: 'Fantasy', 36: 'History',
  27: 'Horror', 10402: 'Music', 9648: 'Mystery', 10749: 'Romance',
  878: 'Science Fiction', 10770: 'TV Movie', 53: 'Thriller', 10752: 'War', 37: 'Western',
};
const GENRE_MAP: Record<number, string> = { ...GENRE_MAP_STATIC };


let _genresFetched = false;
async function ensureGenreMap(): Promise<void> {
  if (_genresFetched) return;
  try {
    const { genres } = await tmdbFetch<{ genres: TMDBGenre[] }>('/genre/movie/list');
    genres.forEach(g => { GENRE_MAP[g.id] = g.name; });
    _genresFetched = true;
  } catch { /* fallback to hardcoded */ }
}

// ─── Mood → genre ID mapping 
export const MOOD_GENRE_MAP: Record<string, number[]> = {
  thrilling: [28, 53],          // Action, Thriller
  emotional: [18, 10749],       // Drama, Romance
  'feel-good': [35, 10751, 12],   // Comedy, Family, Adventure
  'mind-bending': [878, 9648, 14],   // Sci-Fi, Mystery, Fantasy
  dark: [27, 80, 10752],   // Horror, Crime, War
  funny: [35, 16],          // Comedy, Animation
  romantic: [10749, 18],       // Romance, Drama
  adventurous: [12, 14, 878],     // Adventure, Fantasy, Sci-Fi
};

// ─── Image URL helpers ─────────────────────────────────────────────────────────
export function posterUrl(path: string | null, size: 'w185' | 'w342' | 'w500' | 'original' = 'w342'): string {
  if (!path) return '';
  return `${IMAGE_BASE}/${size}${path}`;
}
export function backdropUrl(path: string | null, size: 'w780' | 'w1280' | 'original' = 'w1280'): string {
  if (!path) return '';
  return `${IMAGE_BASE}/${size}${path}`;
}

// ─── Mood derivation ───────────────────────────────────────────────────────────
const _GENRE_MOOD: Record<string, string[]> = {
  Action: ['thrilling', 'intense'], Adventure: ['adventurous', 'epic'],
  Animation: ['feel-good', 'enchanting'], Comedy: ['funny', 'feel-good'],
  Crime: ['dark', 'thrilling'], Documentary: ['thoughtful'],
  Drama: ['emotional', 'thoughtful'], Family: ['feel-good', 'uplifting'],
  Fantasy: ['enchanting', 'adventurous'], Horror: ['dark', 'tense'],
  Mystery: ['mind-bending', 'thrilling'], Romance: ['romantic', 'emotional'],
  'Science Fiction': ['mind-bending', 'epic'], Thriller: ['thrilling', 'intense'],
  War: ['epic', 'intense'],
};
function deriveMood(genres: string[]): string[] {
  const s = new Set<string>();
  genres.forEach(g => (_GENRE_MOOD[g] ?? []).forEach(m => s.add(m)));
  return Array.from(s);
}

// ─── Year from TMDB date string ────────────────────────────────────────────────
function releaseYear(d: string | null): number {
  if (!d) return 0;
  const y = parseInt(d.slice(0, 4), 10);
  return isNaN(y) ? 0 : y;
}

// ─── Currency formatter ────────────────────────────────────────────────────────
function fmtMoney(n: number): string {
  if (!n) return 'N/A';
  if (n >= 1_000_000) return `$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `$${(n / 1_000).toFixed(1)}K`;
  return `$${n}`;
}

// ─── Converters ────────────────────────────────────────────────────────────────
function listItemToMovie(item: TMDBListMovie): Movie {
  const genres = (item.genre_ids ?? []).map(id => GENRE_MAP[id]).filter(Boolean) as string[];
  return {
    id: String(item.id),
    title: item.title,
    poster: posterUrl(item.poster_path, 'w342'),
    backdrop: backdropUrl(item.backdrop_path, 'w1280'),
    genres,
    genreIds: item.genre_ids ?? [],
    rating: Math.round(item.vote_average * 10) / 10,
    voteCount: item.vote_count,
    year: releaseYear(item.release_date),
    releaseDate: item.release_date ?? '',
    runtime: 0,
    synopsis: item.overview ?? '',
    director: '',
    writers: [],
    cast: [],
    budget: '',
    revenue: '',
    language: item.original_language ?? 'en',
    originalLanguage: item.original_language ?? 'en',
    popularity: item.popularity,
    mood: deriveMood(genres),
    streamingOn: [],
  };
}

function appendedToMovie(detail: TMDBMovieAppended): Movie {
  const genres = (detail.genres ?? []).map(g => g.name);
  const director = (detail.credits?.crew ?? []).find(c => c.job === 'Director')?.name ?? '';
  const writers = (detail.credits?.crew ?? [])
    .filter(c => c.department === 'Writing')
    .slice(0, 4)
    .map(c => c.name);
  const cast = (detail.credits?.cast ?? []).slice(0, 10).map(c => c.name);
  const trailer = (detail.videos?.results ?? [])
    .find(v => v.type === 'Trailer' && v.site === 'YouTube' && v.official)
    ?? (detail.videos?.results ?? []).find(v => v.type === 'Trailer' && v.site === 'YouTube');

  const langName =
    detail.spoken_languages?.find(l => l.iso_639_1 === detail.original_language)?.english_name
    ?? detail.original_language;

  return {
    id: String(detail.id),
    title: detail.title,
    poster: posterUrl(detail.poster_path, 'w500'),
    backdrop: backdropUrl(detail.backdrop_path, 'original'),
    genres,
    genreIds: (detail.genres ?? []).map(g => g.id),
    rating: Math.round(detail.vote_average * 10) / 10,
    voteCount: detail.vote_count,
    year: releaseYear(detail.release_date),
    releaseDate: detail.release_date ?? '',
    runtime: detail.runtime ?? 0,
    synopsis: detail.overview ?? '',
    director,
    writers,
    cast,
    budget: fmtMoney(detail.budget),
    revenue: fmtMoney(detail.revenue),
    language: langName,
    originalLanguage: detail.original_language ?? 'en',
    popularity: detail.popularity,
    mood: deriveMood(genres),
    streamingOn: [],
    trailerKey: trailer?.key,
    tagline: detail.tagline,
    status: detail.status,
  };
}

// ─── Result shape ──────────────────────────────────────────────────────────────
export interface MovieListResult {
  movies: Movie[];
  totalPages: number;
  totalResults: number;
}

// ─── Public API ────────────────────────────────────────────────────────────────
export const tmdbService = {
  /** Fetch TMDB genre list (also refreshes the genre map). */
  async getGenres(): Promise<TMDBGenre[]> {
    await ensureGenreMap();
    return Object.entries(GENRE_MAP).map(([id, name]) => ({ id: Number(id), name }));
  },

  /** /trending/movie/week */
  async getTrending(page = 1): Promise<MovieListResult> {
    await ensureGenreMap();
    const data = await tmdbFetch<TMDBPaginatedResponse<TMDBListMovie>>('/trending/movie/week', { page });
    return {
      movies: data.results.map(listItemToMovie),
      totalPages: data.total_pages,
      totalResults: data.total_results,
    };
  },

  /** /movie/popular */
  async getPopular(page = 1): Promise<MovieListResult> {
    await ensureGenreMap();
    const data = await tmdbFetch<TMDBPaginatedResponse<TMDBListMovie>>('/movie/popular', { page });
    return {
      movies: data.results.map(listItemToMovie),
      totalPages: data.total_pages,
      totalResults: data.total_results,
    };
  },

  /** /movie/top_rated */
  async getTopRated(page = 1): Promise<MovieListResult> {
    await ensureGenreMap();
    const data = await tmdbFetch<TMDBPaginatedResponse<TMDBListMovie>>('/movie/top_rated', { page });
    return {
      movies: data.results.map(listItemToMovie),
      totalPages: data.total_pages,
      totalResults: data.total_results,
    };
  },

  /** /movie/upcoming */
  async getUpcoming(page = 1): Promise<MovieListResult> {
    await ensureGenreMap();
    const data = await tmdbFetch<TMDBPaginatedResponse<TMDBListMovie>>('/movie/upcoming', { page });
    return {
      movies: data.results.map(listItemToMovie),
      totalPages: data.total_pages,
      totalResults: data.total_results,
    };
  },

  /** /movie/now_playing */
  async getNowPlaying(page = 1): Promise<MovieListResult> {
    await ensureGenreMap();
    const data = await tmdbFetch<TMDBPaginatedResponse<TMDBListMovie>>('/movie/now_playing', { page });
    return {
      movies: data.results.map(listItemToMovie),
      totalPages: data.total_pages,
      totalResults: data.total_results,
    };
  },

  /** /discover/movie with flexible filters */
  async discover(params: DiscoverParams = {}): Promise<MovieListResult> {
    await ensureGenreMap();
    const data = await tmdbFetch<TMDBPaginatedResponse<TMDBListMovie>>('/discover/movie', {
      page: params.page ?? 1,
      sort_by: params.sortBy ?? 'popularity.desc',
      with_genres: params.genreIds?.length ? params.genreIds.join(',') : undefined,
      'vote_average.gte': params.voteAverageGte,
      'vote_count.gte': params.voteCountGte ?? 50,
      'primary_release_date.gte': params.primaryReleaseDateGte,
      'primary_release_date.lte': params.primaryReleaseDateLte,
      'with_runtime.gte': params.withRuntimeGte,
      'with_runtime.lte': params.withRuntimeLte,
      with_original_language: params.withOriginalLanguage,
      year: params.year,
    });
    return {
      movies: data.results.map(listItemToMovie),
      totalPages: data.total_pages,
      totalResults: data.total_results,
    };
  },

  /** /search/movie */
  async search(query: string, page = 1): Promise<MovieListResult> {
    await ensureGenreMap();
    if (!query.trim()) return { movies: [], totalPages: 0, totalResults: 0 };
    const data = await tmdbFetch<TMDBPaginatedResponse<TMDBListMovie>>('/search/movie', {
      query: query.trim(),
      page,
      include_adult: 'false',
    });
    return {
      movies: data.results.map(listItemToMovie),
      totalPages: data.total_pages,
      totalResults: data.total_results,
    };
  },

  /** /movie/{id}?append_to_response=credits,videos,similar */
  async getMovieDetail(id: string): Promise<{ movie: Movie; similar: Movie[] }> {
    await ensureGenreMap();
    const data = await tmdbFetch<TMDBMovieAppended>(`/movie/${id}`, {
      append_to_response: 'credits,videos,similar',
    });
    const movie = appendedToMovie(data);
    const similar = (data.similar?.results ?? []).slice(0, 12).map(listItemToMovie);
    return { movie, similar };
  },

  /** Simple /movie/{id} — for MovieService.get() backward compat */
  async getMovie(id: string): Promise<Movie> {
    const { movie } = await this.getMovieDetail(id);
    return movie;
  },
};

// ─── Backward-compatible MovieService export (used by existing queryFns) ────────
export const MovieService = {
  get: (id: string) => tmdbService.getMovie(id),
  list: (query?: string, genre?: string) =>
    query
      ? tmdbService.search(query).then(r => r.movies)
      : genre
        ? tmdbService.discover({ genreIds: [Object.entries(GENRE_MAP).find(([, n]) => n === genre)?.[0] as unknown as number].filter(Boolean) }).then(r => r.movies)
        : tmdbService.getPopular().then(r => r.movies),
  recommendations: (mood?: string) =>
    mood && MOOD_GENRE_MAP[mood]
      ? tmdbService.discover({ genreIds: MOOD_GENRE_MAP[mood], sortBy: 'vote_average.desc', voteCountGte: 200 }).then(r => r.movies)
      : tmdbService.getTrending().then(r => r.movies.slice(0, 6)),
};
