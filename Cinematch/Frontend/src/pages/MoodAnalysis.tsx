import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ChevronRight, Zap, Droplets, Sun, Brain, Moon, Smile, Heart, Compass, SmilePlus } from 'lucide-react';
import { movies } from '../data/mockData';
import { MovieCard } from '../components/movie/MovieCard';
import { cn } from '../lib/utils';

const moods = [
  { id: 'thrilling', icon: Zap, label: 'Thrilling', description: 'Edge-of-seat excitement', color: 'bg-ember-500/20 border-ember-500/40 text-ember-300', activeBg: 'bg-ember-500' },
  { id: 'emotional', icon: Droplets, label: 'Emotional', description: 'Feel something deep', color: 'bg-dusk-500/20 border-dusk-500/40 text-dusk-300', activeBg: 'bg-dusk-500' },
  { id: 'feel-good', icon: Sun, label: 'Feel-Good', description: 'Uplifting & cheerful', color: 'bg-gilt-500/20 border-gilt-500/40 text-gilt-300', activeBg: 'bg-gilt-500' },
  { id: 'mind-bending', icon: Brain, label: 'Mind-Bending', description: 'Reality-twisting plots', color: 'bg-purple-500/20 border-purple-500/40 text-purple-300', activeBg: 'bg-purple-500' },
  { id: 'dark', icon: Moon, label: 'Dark & Gritty', description: 'Intense & raw', color: 'bg-void-700/60 border-void-600/60 text-mist-400', activeBg: 'bg-void-600' },
  { id: 'funny', icon: Smile, label: 'Funny', description: 'Laughs guaranteed', color: 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300', activeBg: 'bg-emerald-500' },
  { id: 'romantic', icon: Heart, label: 'Romantic', description: 'Love stories', color: 'bg-pink-500/20 border-pink-500/40 text-pink-300', activeBg: 'bg-pink-500' },
  { id: 'adventurous', icon: Compass, label: 'Adventurous', description: 'Epic journeys', color: 'bg-cyan-500/20 border-cyan-500/40 text-cyan-300', activeBg: 'bg-cyan-500' },
];

export function MoodAnalysis() {
  const [selected, setSelected] = useState<string | null>(null);
  const [step, setStep] = useState<'pick' | 'results'>('pick');

  const results = selected
    ? movies.filter((m) => m.mood.some((md) => md.toLowerCase().includes(selected.toLowerCase()))).slice(0, 6)
    : [];

  const activeMood = moods.find((m) => m.id === selected);

  return (
    <div className="mx-auto max-w-5xl px-6 py-14">
      <AnimatePresence mode="wait">
        {step === 'pick' ? (
          <motion.div
            key="pick"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="mb-10 text-center">
              <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-dusk-500/10">
                <SmilePlus className="h-8 w-8 text-dusk-400" />
              </div>
              <h1 className="font-display text-4xl font-bold text-mist-100">How are you feeling?</h1>
              <p className="mt-2 text-mist-400">Pick a mood and we'll find the perfect film for this moment.</p>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
              {moods.map((mood) => (
                <motion.button
                  key={mood.id}
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                  onClick={() => setSelected(mood.id)}
                  className={cn(
                    'flex flex-col items-center gap-2 rounded-2xl border p-5 text-center transition-all duration-200',
                    selected === mood.id
                      ? 'border-white/30 bg-white/10 ring-2 ring-white/30 shadow-lg'
                      : `${mood.color} border hover:border-white/20`
                  )}
                >
                  <mood.icon className="h-8 w-8 mb-2" />
                  <span className="text-sm font-semibold text-mist-100">{mood.label}</span>
                  <span className="text-xs text-mist-500">{mood.description}</span>
                </motion.button>
              ))}
            </div>

            <div className="mt-8 flex justify-center">
              <button
                disabled={!selected}
                onClick={() => setStep('results')}
                className="flex items-center gap-2 rounded-full bg-ember-500 px-8 py-3.5 text-sm font-bold text-white shadow-lg shadow-ember-500/25 disabled:opacity-40 disabled:cursor-not-allowed transition-all hover:bg-ember-400"
              >
                Find My Movies
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <div className="mb-10">
              <button
                onClick={() => setStep('pick')}
                className="mb-6 text-sm text-mist-500 hover:text-mist-100 transition-colors"
              >
                ← Change mood
              </button>
              <div className="flex items-center gap-3">
                {activeMood && <activeMood.icon className="h-8 w-8 text-mist-300" />}
                <div>
                  <h1 className="font-display text-3xl font-bold text-mist-100">
                    {activeMood?.label} picks
                  </h1>
                  <p className="text-mist-500">Hand-picked for your current vibe</p>
                </div>
              </div>
            </div>

            {results.length > 0 ? (
              <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
                {results.map((movie, i) => (
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
            ) : (
              <div className="glass rounded-2xl p-10 text-center">
                <p className="text-mist-400">No movies matched this mood yet. Try a different one!</p>
                <button onClick={() => setStep('pick')} className="mt-4 text-sm font-medium text-ember-400 hover:text-ember-300">
                  Go back
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}