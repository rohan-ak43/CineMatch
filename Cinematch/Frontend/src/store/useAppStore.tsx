import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { Movie } from '../data/mockData';

interface HistoryEntry {
  movie: Movie;
  watchedAt: Date;
}

interface AppStore {
  favorites: Movie[];
  history: HistoryEntry[];
  toggleFavorite: (movie: Movie) => void;
  isFavorite: (id: string) => boolean;
  addHistory: (movie: Movie) => void;
  clearHistory: () => void;
}

const AppContext = createContext<AppStore | null>(null);

export function AppStoreProvider({ children }: { children: ReactNode }) {
  const [favorites, setFavorites] = useState<Movie[]>([]);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  const toggleFavorite = useCallback((movie: Movie) => {
    setFavorites((prev) =>
      prev.some((m) => m.id === movie.id)
        ? prev.filter((m) => m.id !== movie.id)
        : [...prev, movie]
    );
  }, []);

  const isFavorite = useCallback(
    (id: string) => favorites.some((m) => m.id === id),
    [favorites]
  );

  const addHistory = useCallback((movie: Movie) => {
    setHistory((prev) => {
      const filtered = prev.filter((h) => h.movie.id !== movie.id);
      return [{ movie, watchedAt: new Date() }, ...filtered];
    });
  }, []);

  const clearHistory = useCallback(() => setHistory([]), []);

  return (
    <AppContext.Provider value={{ favorites, history, toggleFavorite, isFavorite, addHistory, clearHistory }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppStore() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppStore must be used inside AppStoreProvider');
  return ctx;
}
