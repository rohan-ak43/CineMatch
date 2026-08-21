import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { createPortal } from 'react-dom';
import { motion } from 'framer-motion';
import { Play, Brain, ChevronRight } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { tmdbService } from '../lib/tmdb';
import type { Movie } from '../data/mockData';
import { MovieCard } from '../components/movie/MovieCard';
import { MovieGridSkeleton } from '../components/ui/LoadingSkeleton';
import { HeroBackgroundSlideshow } from '../components/HeroBackgroundSlideshow';

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

const stagger = {
  show: { transition: { staggerChildren: 0.1 } },
};

const features = [
  {
    title: 'Mood-Aware AI',
    description: "Tell us how you feel and we'll find movies that match your emotional state perfectly.",
  },
  {
    title: 'Smart Recommendations',
    description: 'Our engine learns your taste over time and surfaces hidden gems you\'ll love.',
  },
  {
    title: 'Curated Trending',
    description: "Stay up-to-date with what's popular globally, filtered to your genre preferences.",
  },
];

function MovieRow({
  title,
  subtitle,
  movies,
  isLoading,
}: {
  title: string;
  subtitle: string;
  movies: Movie[];
  isLoading: boolean;
}) {
  return (
    <section className="relative z-10 mx-auto max-w-7xl px-6 py-10">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h2 className="font-display text-2xl font-bold text-mist-100">{title}</h2>
          <p className="mt-1 text-sm text-mist-400">{subtitle}</p>
        </div>
        <Link
          to="/movies"
          className="flex items-center gap-1 text-sm font-medium text-ember-400 hover:text-ember-300 transition-colors"
        >
          See all <ChevronRight className="h-4 w-4" />
        </Link>
      </div>

      {isLoading ? (
        <MovieGridSkeleton count={12} />
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
          {movies.slice(0, 12).map((movie, i) => (
            <motion.div
              key={movie.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <MovieCard movie={movie} />
            </motion.div>
          ))}
        </div>
      )}
    </section>
  );
}

export function Home() {
  const { data: trendingData, isLoading: trendingLoading } = useQuery({
    queryKey: ['trending', 1],
    queryFn: () => tmdbService.getTrending(1),
    staleTime: 5 * 60 * 1000,
  });

  const { data: popularData, isLoading: popularLoading } = useQuery({
    queryKey: ['popular', 1],
    queryFn: () => tmdbService.getPopular(1),
    staleTime: 5 * 60 * 1000,
  });

  const heroImages = (trendingData?.movies ?? [])
    .filter(m => m.backdrop)
    .slice(0, 10)
    .map(m => m.backdrop);

  // Punch through the app wrapper bg so the fixed canvas shows behind everything
  useEffect(() => {
    const appRoot = document.querySelector<HTMLElement>('.flex.min-h-screen');
    const prev = appRoot?.style.background ?? '';
    if (appRoot) appRoot.style.background = 'transparent';
    return () => { if (appRoot) appRoot.style.background = prev; };
  }, []);

  return (
    <>
      {/* Fixed cinematic canvas — truly behind the full viewport */}
      {createPortal(
        <div
          aria-hidden="true"
          style={{ position: 'fixed', inset: 0, zIndex: -1, overflow: 'hidden' }}
        >
          <HeroBackgroundSlideshow images={heroImages} />
          {/* Smooth gradient: image at top, natural fade toward dark at bottom */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              background:
                'linear-gradient(to bottom, transparent 35%, rgba(11,11,15,0.40) 60%, rgba(11,11,15,0.70) 80%, #0B0B0F 100%)',
              pointerEvents: 'none',
            }}
          />
        </div>,
        document.body
      )}

      {/* Page content — floats over the fixed background */}
      <div>
        {/* Hero */}
        <section
          style={{
            minHeight: '88vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <div className="mx-auto w-full max-w-3xl px-6 text-center">
            <motion.div variants={stagger} initial="hidden" animate="show">
              <motion.h1
                variants={fadeUp}
                className="font-display text-5xl font-extrabold tracking-tight text-mist-100 sm:text-6xl lg:text-7xl"
              >
                Find Your <br /> Perfect Film
              </motion.h1>

              <motion.p
                variants={fadeUp}
                className="mx-auto mt-6 max-w-xl text-lg font-medium text-mist-300 sm:text-xl"
              >
                Discover movies tailored to your mood, watch history, and personal taste.
              </motion.p>

              <motion.div variants={fadeUp} className="mt-10 flex flex-wrap justify-center gap-4">
                <Link
                  to="/recommendations"
                  className="flex items-center gap-2 rounded-full bg-ember-500 px-8 py-3.5 text-sm font-semibold text-white shadow-lg shadow-ember-500/20 transition-all hover:scale-[1.03] hover:bg-ember-400"
                >
                  Get Recommendations
                </Link>
                <Link
                  to="/movies"
                  className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-8 py-3.5 text-sm font-semibold text-mist-100 backdrop-blur-md transition-all hover:bg-white/10 hover:border-white/20"
                >
                  <Play className="h-4 w-4" /> Browse All Movies
                </Link>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Subtle section separator */}
        <div className="mx-auto max-w-7xl px-6">
          <div className="h-px w-full bg-white/5" />
        </div>

        {/* Trending Now */}
        <MovieRow
          title="Trending Now"
          subtitle="Most popular picks this week"
          movies={trendingData?.movies ?? []}
          isLoading={trendingLoading}
        />

        {/* Popular Movies */}
        <MovieRow
          title="Popular Movies"
          subtitle="Watched and loved globally right now"
          movies={popularData?.movies ?? []}
          isLoading={popularLoading}
        />

        {/* Transition band into the solid sections below */}
        <div style={{ height: '80px', background: 'linear-gradient(to bottom, transparent, #0B0B0F)' }} />
      </div>

      {/* Mood CTA Banner */}
      <section className="relative mx-6 mb-16 overflow-hidden rounded-3xl border border-white/5 shadow-2xl lg:mx-auto lg:max-w-7xl">
        <div className="absolute inset-0 bg-gradient-to-r from-void-800 to-void-950" />
        <div className="absolute inset-0 bg-[url('/noise.svg')] opacity-[0.15]" />
        <div className="relative px-8 py-12 sm:px-12 md:flex md:items-center md:justify-between">
          <div>
            <h2 className="font-display text-3xl font-extrabold text-white">
              What's your mood today?
            </h2>
            <p className="mt-2 text-white/80">
              Let us pick the perfect film based on how you're feeling right now.
            </p>
          </div>
          <Link
            to="/mood"
            className="mt-6 inline-flex items-center gap-2 rounded-full bg-white px-7 py-3 text-sm font-bold text-void-950 shadow-lg transition-all hover:bg-mist-100 md:mt-0 shrink-0"
          >
            <Brain className="h-4 w-4" /> Analyse My Mood
          </Link>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="mx-auto max-w-7xl px-6 pb-20">
        <div className="mb-10 text-center">
          <h2 className="font-display text-3xl font-bold text-mist-100">Why CReqx?</h2>
          <p className="mt-2 text-mist-500">Built for people who take movies seriously.</p>
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="glass rounded-2xl p-6 card-lift"
            >
              <h3 className="font-display text-lg font-semibold text-mist-100">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-mist-400">{f.description}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </>
  );
}