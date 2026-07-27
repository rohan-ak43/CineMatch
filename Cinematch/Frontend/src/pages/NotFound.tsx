import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Home, Film } from 'lucide-react';

export function NotFound() {
  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center px-6 text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: 'spring', stiffness: 200, damping: 20 }}
        className="mb-8 text-[120px] leading-none select-none"
      >
        🎬
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h1 className="font-display text-8xl font-black text-void-700">404</h1>
        <h2 className="mt-2 font-display text-2xl font-bold text-mist-100">Scene Not Found</h2>
        <p className="mt-3 max-w-sm text-mist-400">
          This page seems to have been cut from the final edit. Let's get you back to something good.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Link
            to="/"
            className="flex items-center gap-2 rounded-full bg-ember-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-ember-500/25"
          >
            <Home className="h-4 w-4" /> Go Home
          </Link>
          <Link
            to="/movies"
            className="flex items-center gap-2 rounded-full border border-white/10 bg-void-800 px-6 py-3 text-sm font-semibold text-mist-100 hover:border-white/20"
          >
            <Film className="h-4 w-4" /> Browse Movies
          </Link>
        </div>
      </motion.div>
    </div>
  );
}