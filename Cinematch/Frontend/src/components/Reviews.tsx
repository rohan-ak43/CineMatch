import { Star, ThumbsUp } from 'lucide-react';

const MOCK_REVIEWS = [
  { id: 1, name: 'Sarah M.', avatar: 'SM', rating: 5, text: 'An absolute masterpiece. One of those films that stays with you for days. The visuals, the score, the performances — everything is perfect.', date: '2 days ago' },
  { id: 2, name: 'James K.', avatar: 'JK', rating: 4, text: 'Beautifully crafted and emotionally resonant. A few pacing issues in the second act, but the payoff is worth every minute.', date: '1 week ago' },
  { id: 3, name: 'Priya R.', avatar: 'PR', rating: 5, text: 'I rarely give 5 stars, but this film earned every one. The director\'s vision is uncompromising and the result is stunning.', date: '2 weeks ago' },
];

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <Star
          key={i}
          className="h-3.5 w-3.5"
          fill={i < rating ? '#f5c842' : 'none'}
          stroke={i < rating ? '#f5c842' : '#6a7296'}
          strokeWidth={1.5}
        />
      ))}
    </div>
  );
}

export function Reviews({ movieId: _ }: { movieId: string }) {
  return (
    <div className="mt-14">
      <h2 className="mb-6 font-display text-lg font-bold text-mist-100">
        Audience Reviews <span className="ml-2 text-sm font-normal text-mist-500">({MOCK_REVIEWS.length})</span>
      </h2>

      <div className="flex flex-col gap-4">
        {MOCK_REVIEWS.map((r) => (
          <div key={r.id} className="glass rounded-2xl p-5">
            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-ember-500 to-dusk-500 text-sm font-bold text-white">
                {r.avatar}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-sm font-semibold text-mist-100">{r.name}</span>
                  <StarRating rating={r.rating} />
                  <span className="text-xs text-mist-500">{r.date}</span>
                </div>
                <p className="mt-2 text-sm leading-relaxed text-mist-300">{r.text}</p>
                <button className="mt-3 flex items-center gap-1.5 text-xs text-mist-500 hover:text-mist-300 transition-colors">
                  <ThumbsUp className="h-3.5 w-3.5" /> Helpful
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
