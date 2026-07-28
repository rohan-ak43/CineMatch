import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Star, ChevronRight, RefreshCw, Film, Disc, Clapperboard, Globe, Zap, Target, Moon, User, Heart, Users, Home } from 'lucide-react';
import { Link } from 'react-router-dom';
import { movies } from '../data/mockData';
import { MovieCard } from '../components/movie/MovieCard';
import { cn } from '../lib/utils';

const questions = [
  {
    id: 'era',
    question: 'Preferred era?',
    options: [
      { value: 'classic', label: 'Classic (Pre-2000)', icon: Film },
      { value: 'modern', label: 'Modern (2000s)', icon: Disc },
      { value: 'recent', label: 'Recent (2015+)', icon: Clapperboard },
      { value: 'any', label: 'Any era', icon: Globe },
    ],
  },
  {
    id: 'length',
    question: 'How long is your evening?',
    options: [
      { value: 'short', label: 'Quick (<90 min)', icon: Zap },
      { value: 'medium', label: 'Standard (90–120 min)', icon: Target },
      { value: 'long', label: 'Epic (120+ min)', icon: Moon },
      { value: 'any', label: 'Doesn\'t matter', icon: Sparkles },
    ],
  },
  {
    id: 'company',
    question: 'Who\'s watching with you?',
    options: [
      { value: 'solo', label: 'Just me', icon: User },
      { value: 'partner', label: 'Date night', icon: Heart },
      { value: 'friends', label: 'Friends', icon: Users },
      { value: 'family', label: 'Family', icon: Home },
    ],
  },
];

export function RecommendationEngine() {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [step, setStep] = useState(0);
  const [showResults, setShowResults] = useState(false);

  const current = questions[step];
  const progress = ((step) / questions.length) * 100;

  const handleAnswer = (value: string) => {
    const newAnswers = { ...answers, [current.id]: value };
    setAnswers(newAnswers);
    if (step < questions.length - 1) {
      setStep(step + 1);
    } else {
      setShowResults(true);
    }
  };

  const reset = () => {
    setAnswers({});
    setStep(0);
    setShowResults(false);
  };

  // Filter based on answers
  const results = (() => {
    let result = [...movies];
    if (answers.era === 'classic') result = result.filter((m) => m.year < 2000);
    else if (answers.era === 'modern') result = result.filter((m) => m.year >= 2000 && m.year < 2015);
    else if (answers.era === 'recent') result = result.filter((m) => m.year >= 2015);

    if (answers.length === 'short') result = result.filter((m) => m.runtime < 90);
    else if (answers.length === 'medium') result = result.filter((m) => m.runtime >= 90 && m.runtime <= 120);
    else if (answers.length === 'long') result = result.filter((m) => m.runtime > 120);

    if (answers.company === 'partner') result = result.filter((m) => m.genres.some((g) => ['Romance', 'Drama'].includes(g)));
    else if (answers.company === 'friends') result = result.filter((m) => m.genres.some((g) => ['Comedy', 'Action', 'Thriller'].includes(g)));
    else if (answers.company === 'family') result = result.filter((m) => m.genres.some((g) => ['Animation', 'Adventure', 'Comedy'].includes(g)));

    return result.length > 0 ? result : movies.slice(0, 6);
  })();

  return (
    <div className="mx-auto max-w-3xl px-6 py-14">
      <AnimatePresence mode="wait">
        {!showResults ? (
          <motion.div
            key={`step-${step}`}
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -40 }}
            transition={{ duration: 0.3 }}
          >
            {/* Progress */}
            <div className="mb-10">
              <div className="mb-4 flex items-center justify-between text-sm">
                <span className="text-mist-500">Question {step + 1} of {questions.length}</span>
                <span className="flex items-center gap-1.5 text-ember-400 font-semibold">
                  Recommendation Engine
                </span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-void-700 overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-ember-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.4 }}
                />
              </div>
            </div>

            <h1 className="font-display text-3xl font-bold text-mist-100 mb-8">{current.question}</h1>

            <div className="grid grid-cols-2 gap-3">
              {current.options.map((opt) => (
                <motion.button
                  key={opt.value}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleAnswer(opt.value)}
                  className="flex flex-col items-center gap-2 rounded-2xl border border-white/10 bg-void-800/60 p-6 text-center hover:border-ember-500/40 hover:bg-ember-500/5 transition-all"
                >
                  <opt.icon className="h-8 w-8 mb-2" />
                  <span className="text-sm font-semibold text-mist-100">{opt.label}</span>
                </motion.button>
              ))}
            </div>

            {step > 0 && (
              <button
                onClick={() => setStep(step - 1)}
                className="mt-6 text-sm text-mist-500 hover:text-mist-100 transition-colors"
              >
                ← Back
              </button>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="mb-8 flex items-center justify-between">
              <div>
                <h1 className="font-display text-3xl font-bold text-mist-100">
                  
                  Your Picks
                </h1>
                <p className="mt-1 text-mist-500">{results.length} perfect matches for you</p>
              </div>
              <button
                onClick={reset}
                className="flex items-center gap-1.5 rounded-full border border-white/10 bg-void-800 px-4 py-2 text-sm text-mist-400 hover:text-mist-100 transition-colors"
              >
                <RefreshCw className="h-3.5 w-3.5" /> Start over
              </button>
            </div>

            <div className="grid grid-cols-2 gap-5 sm:grid-cols-3">
              {results.slice(0, 6).map((movie, i) => (
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

            <div className="mt-10 text-center">
              <Link
                to="/movies"
                className="inline-flex items-center gap-2 text-sm font-medium text-ember-400 hover:text-ember-300 transition-colors"
              >
                Browse all movies <ChevronRight className="h-4 w-4" />
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}