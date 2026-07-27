import { motion } from 'framer-motion';
import { Clock, Trash2, Link as LinkIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAppStore } from '../store/useAppStore';
import { EmptyState } from '../components/ui/States';
import { Star } from 'lucide-react';

function timeAgo(date: Date): string {
  const diff = Date.now() - date.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function WatchHistory() {
  const { history, clearHistory } = useAppStore();

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <div className="mb-8 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-dusk-500/10">
            <Clock className="h-5 w-5 text-dusk-400" />
          </div>
          <div>
            <h1 className="font-display text-3xl font-bold text-mist-100">Watch History</h1>
            <p className="text-sm text-mist-500">{history.length} film{history.length !== 1 ? 's' : ''} watched</p>
          </div>
        </div>

        {history.length > 0 && (
          <button
            onClick={clearHistory}
            className="flex items-center gap-1.5 rounded-full bg-void-800 px-4 py-2 text-xs font-medium text-mist-400 ring-1 ring-white/10 hover:text-ember-400 hover:ring-ember-500/30 transition-all"
          >
            <Trash2 className="h-3.5 w-3.5" /> Clear all
          </button>
        )}
      </div>

      {history.length === 0 ? (
        <EmptyState
          icon={Clock}
          title="No watch history yet"
          description="Movies you add to your history will appear here."
          action={{ label: 'Discover Movies', to: '/movies' }}
        />
      ) : (
        <div className="flex flex-col gap-3">
          {history.map((entry, i) => (
            <motion.div
              key={`${entry.movie.id}-${i}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.06 }}
              className="glass flex items-center gap-4 rounded-2xl p-4"
            >
              <Link to={`/movies/${entry.movie.id}`} className="shrink-0">
                <img
                  src={entry.movie.poster}
                  alt={entry.movie.title}
                  className="h-20 w-14 rounded-lg object-cover ring-1 ring-white/10"
                />
              </Link>

              <div className="min-w-0 flex-1">
                <Link
                  to={`/movies/${entry.movie.id}`}
                  className="font-display font-semibold text-mist-100 hover:text-ember-400 transition-colors truncate block"
                >
                  {entry.movie.title}
                </Link>
                <p className="mt-0.5 text-xs text-mist-500">{entry.movie.year} · {entry.movie.genres.slice(0, 2).join(', ')}</p>
                <div className="mt-1 flex items-center gap-1">
                  <Star className="h-3 w-3 fill-gilt-400 text-gilt-400" strokeWidth={0} />
                  <span className="text-xs font-medium text-gilt-400">{entry.movie.rating.toFixed(1)}</span>
                </div>
              </div>

              <div className="shrink-0 text-right">
                <p className="text-xs text-mist-500">{timeAgo(entry.watchedAt)}</p>
                <Link
                  to={`/movies/${entry.movie.id}`}
                  className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-ember-400 hover:text-ember-300 transition-colors"
                >
                  Details <LinkIcon className="h-3 w-3" />
                </Link>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}