import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, X } from 'lucide-react';
import { cn } from '../lib/utils';

interface SearchBarProps {
  compact?: boolean;
}

export function SearchBar({ compact }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [focused, setFocused] = useState(false);
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);

  // Keyboard shortcut: Ctrl+K / Cmd+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
      setQuery('');
      inputRef.current?.blur();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div
        className={cn(
          'flex items-center gap-2 rounded-full transition-all duration-200',
          'bg-void-800/80 ring-1 ring-white/10',
          compact ? 'px-3 py-1.5' : 'px-4 py-2.5',
          focused && 'ring-ember-500/50 bg-void-800'
        )}
      >
        <Search className={cn('shrink-0 text-mist-500', compact ? 'h-3.5 w-3.5' : 'h-4 w-4')} />
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder={compact ? 'Search…' : 'Search movies, genres, directors…'}
          className={cn(
            'flex-1 bg-transparent text-mist-100 placeholder:text-mist-500 focus:outline-none',
            compact ? 'text-xs' : 'text-sm'
          )}
          aria-label="Search movies"
        />
        {query && (
          <button
            type="button"
            onClick={() => setQuery('')}
            className="text-mist-500 hover:text-mist-300 transition-colors"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        )}
        {!compact && !query && (
          <kbd className="hidden sm:flex items-center gap-0.5 rounded-md bg-void-700 px-1.5 py-0.5 text-[10px] text-mist-500 font-mono shrink-0">
            ⌘K
          </kbd>
        )}
      </div>
    </form>
  );
}
