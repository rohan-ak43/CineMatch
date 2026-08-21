import { Link } from 'react-router-dom';
import { Heart, Star } from 'lucide-react';
import type { Movie } from '../../data/mockData';
import { useAppStore } from '../../store/useAppStore';
import { toast } from '../ui/Toast';
import { cn } from '../../lib/utils';

interface MovieCardProps {
  movie: Movie;
}

const FALLBACK_POSTER = 'data:image/svg+xml,%3Csvg xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22 width%3D%22100%22 height%3D%22150%22 viewBox%3D%220 0 100 150%22%3E%3Crect width%3D%22100%22 height%3D%22150%22 fill%3D%22%231a1a2e%22%2F%3E%3Ctext x%3D%2250%22 y%3D%2275%22 text-anchor%3D%22middle%22 fill%3D%22%23555%22 font-size%3D%2212%22%3ENo Image%3C%2Ftext%3E%3C%2Fsvg%3E';

export function MovieCard({ movie }: MovieCardProps) {
  const { isFavorite, toggleFavorite } = useAppStore();
  const fav = isFavorite(movie.id);
  const firstGenre = movie.genres[0] ?? '';
  const displayRating = movie.rating > 0 ? movie.rating.toFixed(1) : '—';
  const displayYear = movie.year > 0 ? movie.year : '';

  return (
    <div className="group relative card-lift">
      <Link to={`/movies/${movie.id}`} className="block">
        <div className="relative overflow-hidden rounded-xl aspect-[2/3] bg-void-800">
          <img
            src={movie.poster || FALLBACK_POSTER}
            alt={movie.title}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
            onError={(e) => { e.currentTarget.src = FALLBACK_POSTER; }}
          />
          {/* Hover overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-void-950 via-void-950/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

          {/* Rating badge */}
          {movie.rating > 0 && (
            <div className="absolute top-2 left-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-xs font-semibold backdrop-blur-sm">
              <Star className="h-3 w-3 fill-gilt-400 text-gilt-400" strokeWidth={0} />
              <span className="text-mist-100">{displayRating}</span>
            </div>
          )}

          {/* Genre tag */}
          {firstGenre && (
            <div className="absolute top-2 right-2 rounded-full bg-ember-500/80 px-2 py-0.5 text-[10px] font-semibold text-white backdrop-blur-sm max-w-[80px] truncate">
              {firstGenre}
            </div>
          )}
        </div>
      </Link>

      {/* Favorite button */}
      <button
        aria-label={fav ? 'Remove from favorites' : 'Add to favorites'}
        onClick={(e) => {
          e.preventDefault();
          toggleFavorite(movie);
          toast(fav ? `Removed from favorites` : `Added to favorites`);
        }}
        className={cn(
          'absolute bottom-12 right-2 flex h-8 w-8 items-center justify-center rounded-full shadow-lg transition-all duration-200',
          'opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0',
          fav ? 'bg-ember-500 text-white' : 'bg-void-800/90 text-mist-300 hover:text-ember-400 ring-1 ring-white/10'
        )}
      >
        <Heart className="h-4 w-4" fill={fav ? 'currentColor' : 'none'} />
      </button>

      {/* Title + year */}
      <div className="mt-2 px-0.5">
        <p className="text-sm font-medium text-mist-100 truncate">{movie.title}</p>
        <p className="text-xs text-mist-500">{displayYear}</p>
      </div>
    </div>
  );
}
