// ─── Raw TMDB API response types ──────────────────────────────────────────────

export interface TMDBGenre {
  id: number;
  name: string;
}

/** Shape of each item in list/search/discover responses */
export interface TMDBListMovie {
  id: number;
  title: string;
  overview: string;
  poster_path: string | null;
  backdrop_path: string | null;
  genre_ids: number[];
  vote_average: number;
  vote_count: number;
  release_date: string;
  original_language: string;
  popularity: number;
  adult: boolean;
  video: boolean;
}

/** Paginated envelope returned by most list endpoints */
export interface TMDBPaginatedResponse<T> {
  page: number;
  results: T[];
  total_pages: number;
  total_results: number;
}

/** Genre object inside a detail response */
export interface TMDBGenreDetail {
  id: number;
  name: string;
}

/** Spoken language inside a detail response */
export interface TMDBSpokenLanguage {
  english_name: string;
  iso_639_1: string;
  name: string;
}

/** Full movie detail response (/movie/{id}) */
export interface TMDBMovieDetail {
  id: number;
  title: string;
  overview: string;
  tagline: string;
  status: string;
  poster_path: string | null;
  backdrop_path: string | null;
  genres: TMDBGenreDetail[];
  vote_average: number;
  vote_count: number;
  release_date: string;
  runtime: number | null;
  budget: number;
  revenue: number;
  original_language: string;
  spoken_languages: TMDBSpokenLanguage[];
  popularity: number;
  homepage: string | null;
  imdb_id: string | null;
}

/** Cast member from /movie/{id}/credits */
export interface TMDBCastMember {
  id: number;
  name: string;
  character: string;
  profile_path: string | null;
  order: number;
}

/** Crew member from /movie/{id}/credits */
export interface TMDBCrewMember {
  id: number;
  name: string;
  job: string;
  department: string;
  profile_path: string | null;
}

export interface TMDBCreditsResponse {
  id: number;
  cast: TMDBCastMember[];
  crew: TMDBCrewMember[];
}

/** Video (trailer) from /movie/{id}/videos */
export interface TMDBVideo {
  id: string;
  key: string;
  name: string;
  site: string; // 'YouTube' | 'Vimeo'
  type: string; // 'Trailer' | 'Teaser' | 'Clip' | ...
  official: boolean;
  published_at: string;
}

export interface TMDBVideosResponse {
  id: number;
  results: TMDBVideo[];
}

/** Append-to-response composite for /movie/{id}?append_to_response=credits,videos,similar */
export interface TMDBMovieAppended extends TMDBMovieDetail {
  credits: TMDBCreditsResponse;
  videos: TMDBVideosResponse;
  similar: TMDBPaginatedResponse<TMDBListMovie>;
}

/** Parameters for /discover/movie */
export interface DiscoverParams {
  page?: number;
  genreIds?: number[];
  sortBy?: string;
  voteAverageGte?: number;
  voteCountGte?: number;
  primaryReleaseDateGte?: string;
  primaryReleaseDateLte?: string;
  withRuntimeGte?: number;
  withRuntimeLte?: number;
  withOriginalLanguage?: string;
  year?: number;
}
