import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Play, Sparkles, Brain, Star, ChevronRight, TrendingUp } from 'lucide-react';
import { movies } from '../data/mockData';
import { MovieCard } from '../components/movie/MovieCard';

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
    description: 'Tell us how you feel and we\'ll find movies that match your emotional state perfectly.',
  },
  {
    title: 'Smart Recommendations',
    description: 'Our engine learns your taste over time and surfaces hidden gems you\'ll love.',
  },
  {
    title: 'Curated Trending',
    description: 'Stay up-to-date with what\'s popular globally, filtered to your genre preferences.',
  },
];

const heroMovie = movies[0];
const trending = movies.slice(0, 6);

export function Home() {
  return (
    <div>
      {/* ── Hero ── */}
      <section className="relative min-h-[88vh] flex items-end overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 -z-10">
          <img
            src={heroMovie.backdrop}
            alt=""
            className="h-full w-full object-cover opacity-30"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-void-950 via-void-950/80 to-void-950/20" />
          <div className="absolute inset-0 bg-gradient-to-t from-void-950 via-transparent to-void-950/40" />
        </div>

        {/* Floating particles */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full bg-ember-500/20"
              style={{
                width: `${Math.random() * 200 + 60}px`,
                height: `${Math.random() * 200 + 60}px`,
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                filter: 'blur(60px)',
              }}
              animate={{
                x: [0, 30, -20, 0],
                y: [0, -20, 30, 0],
                opacity: [0.2, 0.5, 0.2],
              }}
              transition={{
                duration: 8 + i * 2,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
          ))}
        </div>

        <div className="mx-auto w-full max-w-7xl px-6 pb-20 pt-24">
          <motion.div
            variants={stagger}
            initial="hidden"
            animate="show"
            className="max-w-2xl"
          >


            <motion.h1
              variants={fadeUp}
              className="font-display text-5xl font-extrabold leading-tight text-mist-100 sm:text-6xl lg:text-7xl"
            >
              Find Your
              <span className="block text-ember-400">Perfect Film</span>
            </motion.h1>

            <motion.p
              variants={fadeUp}
              className="mt-5 max-w-xl text-lg leading-relaxed text-mist-300"
            >
              CineMatch learns your taste, reads your mood, and recommends movies you'll actually love — not just what's trending.
            </motion.p>

            <motion.div variants={fadeUp} className="mt-8 flex flex-wrap gap-4">
              <Link
                to="/recommendations"
                className="btn-glow flex items-center gap-2 rounded-full bg-ember-500 px-7 py-3.5 text-sm font-bold text-white shadow-lg shadow-ember-500/25 transition-all"
              >
                <Sparkles className="h-4 w-4" /> Get Recommendations
              </Link>
              <Link
                to="/movies"
                className="flex items-center gap-2 rounded-full border border-white/10 bg-void-800/60 px-7 py-3.5 text-sm font-semibold text-mist-100 backdrop-blur-sm hover:border-white/20 transition-all"
              >
                <Play className="h-4 w-4" /> Browse All Movies
              </Link>
            </motion.div>

            <motion.div variants={fadeUp} className="mt-10 flex items-center gap-6">
              <div className="flex -space-x-2">
                {['S', 'M', 'A', 'R'].map((l, i) => (
                  <div
                    key={i}
                    className="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold text-white ring-2 ring-void-950"
                    style={{ background: ['#e8491f', '#5847c8', '#f5c842', '#06b6d4'][i] }}
                  >
                    {l}
                  </div>
                ))}
              </div>
              <div className="text-sm text-mist-400">
                <span className="font-semibold text-mist-100">10,000+</span> movies curated for you
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ── Trending Now ── */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h2 className="font-display text-2xl font-bold text-mist-100">Trending Now</h2>
            <p className="mt-1 text-sm text-mist-500">Most popular picks this week</p>
          </div>
          <Link
            to="/movies"
            className="flex items-center gap-1 text-sm font-medium text-ember-400 hover:text-ember-300 transition-colors"
          >
            See all <ChevronRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
          {trending.map((movie, i) => (
            <motion.div
              key={movie.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
            >
              <MovieCard movie={movie} />
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Mood CTA Banner ── */}
      <section className="relative mx-6 mb-16 overflow-hidden rounded-3xl border border-white/5 shadow-2xl lg:mx-auto lg:max-w-7xl">
        <div className="absolute inset-0 bg-gradient-to-r from-void-800 to-void-950" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-[0.15]" />
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
          <h2 className="font-display text-3xl font-bold text-mist-100">Why CineMatch?</h2>
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
    </div>
  );
}