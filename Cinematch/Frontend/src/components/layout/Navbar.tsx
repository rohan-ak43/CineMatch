import { useEffect, useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { Clapperboard, Menu, X, User } from 'lucide-react';
import { AnimatePresence, motion } from 'framer-motion';
import { SearchBar } from '../SearchBar';
import { cn } from '../../lib/utils';

const links = [
    { to: '/', label: 'Home' },
    { to: '/movies', label: 'Movies' },
    { to: '/recommendations', label: 'Recommendations' },
    { to: '/mood', label: 'Mood Analysis' },
    { to: '/history', label: 'Watch History' },
    { to: '/favorites', label: 'Favorites' },
];

export function Navbar() {
    const [scrolled, setScrolled] = useState(false);
    const [open, setOpen] = useState(false);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 12);
        window.addEventListener('scroll', onScroll);
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    return (
        <header
            className={cn(
                'sticky top-0 z-50 transition-all duration-300',
                scrolled ? 'bg-void-950/70 backdrop-blur-xl border-b border-white/10' : 'bg-transparent border-b border-transparent'
            )}
        >
            <nav className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
                <Link to="/" className="flex items-center gap-2 shrink-0">
                    <Clapperboard className="h-6 w-6 text-ember-500" />
                    <span className="font-display text-lg font-bold tracking-tight text-mist-100">
                        Cine<span className="text-ember-500">Match</span>
                    </span>
                </Link>

                <div className="hidden items-center gap-1 xl:flex">
                    {links.map((l) => (
                        <NavLink
                            key={l.to}
                            to={l.to}
                            end={l.to === '/'}
                            className={({ isActive }) =>
                                cn(
                                    'rounded-full px-3 py-1.5 text-sm font-medium transition-colors',
                                    isActive ? 'bg-white/10 text-white shadow-sm' : 'text-mist-300 hover:text-white hover:bg-white/5'
                                )
                            }
                        >
                            {l.label}
                        </NavLink>
                    ))}
                </div>

                <div className="hidden flex-1 items-center justify-end gap-3 md:flex">
                    <div className="max-w-xs flex-1">
                        <SearchBar compact />
                    </div>
                    <Link
                        to="/profile"
                        aria-label="Profile"
                        className="flex h-9 w-9 items-center justify-center rounded-full bg-white/5 ring-1 ring-white/10 hover:bg-white/10 transition-colors"
                    >
                        <User className="h-4 w-4 text-mist-100" />
                    </Link>
                </div>

                <button
                    aria-label={open ? 'Close menu' : 'Open menu'}
                    onClick={() => setOpen((v) => !v)}
                    className="rounded-lg p-2 text-mist-100 xl:hidden"
                >
                    {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </button>
            </nav>


            <AnimatePresence>
                {open && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden bg-void-950/80 backdrop-blur-2xl border-b border-white/10 xl:hidden"
                    >
                        <div className="flex flex-col gap-1 px-4 pb-4 pt-2">
                            <SearchBar />
                            {links.map((l) => (
                                <NavLink
                                    key={l.to}
                                    to={l.to}
                                    end={l.to === '/'}
                                    onClick={() => setOpen(false)}
                                    className={({ isActive }) =>
                                        cn('rounded-lg px-3 py-2 text-sm font-medium transition-colors', isActive ? 'bg-white/10 text-white' : 'text-mist-300 hover:text-white hover:bg-white/5')
                                    }
                                >
                                    {l.label}
                                </NavLink>
                            ))}
                            <NavLink to="/profile" onClick={() => setOpen(false)} className="rounded-lg px-3 py-2 text-sm font-medium text-mist-300">
                                Profile
                            </NavLink>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </header>
    );
}