import { movies, type Movie } from '../data/mockData';

export const MovieService = {
  get: async (id: string): Promise<Movie> => {
    await new Promise((r) => setTimeout(r, 300));
    const movie = movies.find((m) => m.id === id);
    if (!movie) throw new Error(`Movie ${id} not found`);
    return movie;
  },

  list: async (query?: string, genre?: string): Promise<Movie[]> => {
    await new Promise((r) => setTimeout(r, 200));
    let result = [...movies];
    if (query) {
      const q = query.toLowerCase();
      result = result.filter(
        (m) =>
          m.title.toLowerCase().includes(q) ||
          m.genres.some((g) => g.toLowerCase().includes(q)) ||
          m.director.toLowerCase().includes(q)
      );
    }
    if (genre) {
      result = result.filter((m) => m.genres.includes(genre));
    }
    return result;
  },

  recommendations: async (mood?: string): Promise<Movie[]> => {
    await new Promise((r) => setTimeout(r, 400));
    if (!mood) return movies.slice(0, 6);
    return movies.filter((m) => m.mood.some((md) => md.toLowerCase().includes(mood.toLowerCase()))).slice(0, 6);
  },
};
