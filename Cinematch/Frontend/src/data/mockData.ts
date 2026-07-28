// ─── App-level Movie type ──────────────────────────────────────────────────────
// This is the canonical Movie type used across components, store, and pages.
// It is populated from TMDB API data via the tmdb service converter functions.

export interface Movie {
  id: string;            // String version of TMDB numeric id
  title: string;
  poster: string;        // Full CDN URL (w342 for cards, w500 for detail)
  backdrop: string;      // Full CDN URL (w1280 / original)
  genres: string[];      // Human-readable genre names
  genreIds: number[];    // TMDB genre IDs (for discover queries)
  rating: number;        // vote_average (0–10)
  voteCount: number;
  year: number;          // Parsed from release_date
  releaseDate: string;   // ISO date string YYYY-MM-DD
  runtime: number;       // Minutes; 0 when not fetched (list view)
  synopsis: string;      // overview
  director: string;      // From credits; '' for list items
  writers: string[];
  cast: string[];        // Top 8 cast names; [] for list items
  budget: string;        // Formatted, e.g. '$165.0M'; '' for list items
  revenue: string;
  language: string;      // English name of primary spoken language
  originalLanguage: string; // ISO 639-1 code
  popularity: number;
  mood: string[];        // Derived from genres for backward compat
  streamingOn: string[]; // Empty — TMDB Watch Providers API is premium tier
  // Detail-only optional fields
  trailerKey?: string;   // YouTube video key
  tagline?: string;
  status?: string;
}

/** Generates a human-readable explanation for a recommendation. */
export function explainableFor(movie: Movie, _watched: Movie[]): string {
  const reasons = [
    `Because you enjoy ${movie.genres[0] ?? 'great'} films with strong storytelling`,
    `Highly rated (${movie.rating}/10) with critically acclaimed performances`,
    `A fan favourite across multiple genre preferences similar to yours`,
    `Popular on TMDB with ${movie.voteCount.toLocaleString()} ratings worldwide`,
  ];
  const idx = movie.id.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0) % reasons.length;
  return reasons[idx];
}
