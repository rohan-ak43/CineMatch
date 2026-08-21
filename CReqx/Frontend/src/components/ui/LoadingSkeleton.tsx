import { cn } from '../../lib/utils';

interface ShimmerProps {
  className?: string;
}

export function Shimmer({ className }: ShimmerProps) {
  return <div className={cn('shimmer', className)} />;
}

export function MovieCardSkeleton() {
  return (
    <div className="flex flex-col gap-2">
      <Shimmer className="aspect-[2/3] w-full rounded-xl" />
      <Shimmer className="h-4 w-3/4 rounded" />
      <Shimmer className="h-3 w-1/2 rounded" />
    </div>
  );
}

export function MovieGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
      {Array.from({ length: count }).map((_, i) => (
        <MovieCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function HeroSkeleton() {
  return (
    <div className="relative h-[70vh] w-full overflow-hidden">
      <Shimmer className="h-full w-full rounded-none" />
    </div>
  );
}