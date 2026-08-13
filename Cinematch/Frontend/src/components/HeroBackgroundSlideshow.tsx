import { useState, useEffect } from 'react';

interface HeroBackgroundSlideshowProps {
  /** Full image URLs to cycle through. Pass poster or backdrop URLs. */
  images: string[];
}

const INTERVAL_MS = 5500;

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function HeroBackgroundSlideshow({ images }: HeroBackgroundSlideshowProps) {
  const [shuffled, setShuffled] = useState<string[]>([]);
  const [current, setCurrent] = useState(0);

  // Re-shuffle whenever the image list changes (e.g. after the async TMDB fetch resolves)
  useEffect(() => {
    const filtered = images.filter(Boolean);
    if (filtered.length === 0) return;
    setShuffled(shuffle(filtered));
    setCurrent(0);
  }, [images]);

  useEffect(() => {
    if (shuffled.length === 0) return;
    const timer = setInterval(() => {
      setCurrent((prev) => (prev + 1) % shuffled.length);
    }, INTERVAL_MS);
    return () => clearInterval(timer);
  }, [shuffled]);

  if (shuffled.length === 0) {
    return (
      <div
        aria-hidden="true"
        style={{ position: 'absolute', inset: 0, zIndex: 0, backgroundColor: '#0B0B0F' }}
      />
    );
  }

  return (
    <div
      aria-hidden="true"
      style={{ position: 'absolute', inset: 0, zIndex: 0, overflow: 'hidden', backgroundColor: '#0B0B0F' }}
    >
      {shuffled.map((src, i) => (
        <img
          key={src}
          src={src}
          alt=""
          style={{
            position: 'absolute',
            inset: 0,
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            objectPosition: 'center',
            opacity: i === current ? 1 : 0,
            animation: i === current ? `kenBurns ${INTERVAL_MS}ms ease-in-out forwards` : 'none',
            transition: 'opacity 1.5s ease-in-out',
            filter: 'saturate(0.7)',
            willChange: 'opacity, transform',
          }}
        />
      ))}

      {/* Dark overlay for text readability */}
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(0, 0, 0, 0.58)' }} />

      {/* Cinematic vignette */}
      <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at center, transparent 35%, rgba(0,0,0,0.5) 100%)' }} />

      {/* Bottom fade into page */}
      <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: '200px', background: 'linear-gradient(to top, #0B0B0F, transparent)' }} />

      <style>{`
        @keyframes kenBurns {
          from { transform: scale(1.0) translate(0, 0); }
          to   { transform: scale(1.08) translate(-1%, -0.5%); }
        }
      `}</style>
    </div>
  );
}
