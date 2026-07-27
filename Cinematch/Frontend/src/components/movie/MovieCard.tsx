import { Link } from 'react-router-dom';
import { Heart, Star } from 'lucide-react';
import type { Movie } from '../../data/mockData';
import { useAppStore } from '../../store/useAppStore';
import { toast } from '../ui/Toast';
import { cn } from '../../lib/utils';

interface MovieCardProps {
  movie: Movie;
}

export function MovieCard({ movie }: MovieCardProps) {
  const { isFavorite, toggleFavorite } = useAppStore();
  const fav = isFavorite(movie.id);

  return (
    <div className="group relative card-lift">
      <Link to={`/movies/${movie.id}`} className="block">
        <div className="relative overflow-hidden rounded-xl aspect-[2/3] bg-void-800">
          <img
            src={movie.poster}
            alt={movie.title}
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
          />
          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-gradient-to-t from-void-950 via-void-950/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

          {/* Rating badge */}
          <div className="absolute top-2 left-2 flex items-center gap-1 rounded-full bg-black/60 px-2 py-0.5 text-xs font-semibold backdrop-blur-sm">
            <Star className="h-3 w-3 fill-gilt-400 text-gilt-400" strokeWidth={0} />
            <span className="text-mist-100">{movie.rating.toFixed(1)}</span>
          </div>

          {/* Genre tag */}
          <div className="absolute top-2 right-2 rounded-full bg-ember-500/80 px-2 py-0.5 text-[10px] font-semibold text-white backdrop-blur-sm">
            {movie.genres[0]}
          </div>
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
        <p className="text-xs text-mist-500">{movie.year}</p>
      </div>
    </div>
  );
}
