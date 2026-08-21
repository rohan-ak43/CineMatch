import { Link } from 'react-router-dom';
import { Clapperboard, ExternalLink, Globe2, Heart } from 'lucide-react';

const footerLinks = {
  Discover: [
    { label: 'Home', to: '/' },
    { label: 'Movies', to: '/movies' },
    { label: 'Mood Analysis', to: '/mood' },
    { label: 'Recommendations', to: '/recommendations' },
  ],
  Account: [
    { label: 'Profile', to: '/profile' },
    { label: 'Favorites', to: '/favorites' },
    { label: 'Watch History', to: '/history' },
    { label: 'Dashboard', to: '/dashboard' },
  ],
};

export function Footer() {
  return (
    <footer className="border-t border-white/5 bg-void-950/80 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center gap-2">
              <Clapperboard className="h-6 w-6 text-ember-500" />
              <span className="font-display text-lg font-bold text-mist-100">
                CR<span className="text-ember-500">eqx</span>
              </span>
            </Link>
            <p className="mt-3 max-w-xs text-sm leading-relaxed text-mist-500">
              Discover your next favourite film. AI-powered recommendations tuned to your mood, taste, and watch history.
            </p>
            <div className="mt-5 flex gap-3">
              <a
                href="https://github.com/rohan-ak43"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub"
                className="flex h-9 w-9 items-center justify-center rounded-full bg-void-800 text-mist-400 ring-1 ring-white/10 hover:text-mist-100 hover:ring-white/20 transition-all"
              >
                <ExternalLink className="h-4 w-4" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Twitter"
                className="flex h-9 w-9 items-center justify-center rounded-full bg-void-800 text-mist-400 ring-1 ring-white/10 hover:text-mist-100 hover:ring-white/20 transition-all"
              >
                <Globe2 className="h-4 w-4" />
              </a>
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(footerLinks).map(([group, links]) => (
            <div key={group}>
              <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-mist-400">
                {group}
              </h3>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link.to}>
                    <Link
                      to={link.to}
                      className="text-sm text-mist-500 hover:text-mist-100 transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

      </div>
    </footer>
  );
}