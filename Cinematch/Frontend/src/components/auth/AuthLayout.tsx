import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Clapperboard } from 'lucide-react';

export function AuthLayout({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
    return (
        <div className="relative flex min-h-[calc(100vh-64px)] items-center justify-center overflow-hidden px-6 py-16">
            <div className="pointer-events-none absolute inset-0 -z-10">
                <img
                    src="https://picsum.photos/seed/auth-backdrop/1600/1000"
                    alt=""
                    className="h-full w-full object-cover opacity-25"
                />
                <div className="absolute inset-0 bg-gradient-to-b from-void-950/60 via-void-950/90 to-void-950" />
            </div>

            <div className="glass w-full max-w-sm rounded-3xl p-8 shadow-2xl shadow-black/40">
                <Link to="/" className="mb-6 flex items-center justify-center gap-2">
                    <Clapperboard className="h-6 w-6 text-ember-500" />
                    <span className="font-display text-lg font-bold text-mist-100">
                        Cine<span className="text-ember-500">Match</span>
                    </span>
                </Link>
                <h1 className="text-center font-display text-xl font-bold text-mist-100">{title}</h1>
                <p className="mt-1 text-center text-sm text-mist-500">{subtitle}</p>
                <div className="mt-6">{children}</div>
            </div>
        </div>
    );
}

export function SocialAuthButtons() {
    return (
        <div className="mt-4 grid grid-cols-2 gap-3">
            <button
                type="button"
                className="rounded-full bg-void-800 py-2.5 text-xs font-semibold text-mist-100 ring-1 ring-white/10 hover:ring-white/20"
            >
                Continue with Google
            </button>
            <button
                type="button"
                className="rounded-full bg-void-800 py-2.5 text-xs font-semibold text-mist-100 ring-1 ring-white/10 hover:ring-white/20"
            >
                Continue with GitHub
            </button>
        </div>
    );
}