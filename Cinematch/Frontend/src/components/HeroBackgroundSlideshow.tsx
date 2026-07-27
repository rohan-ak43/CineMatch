import { useState, useEffect } from 'react';
import { movies } from '../data/mockData';

// Use both poster and backdrop URLs for variety
// Prefer poster (portrait) images for a more cinematic, rich look
const ALL_IMAGES = movies.map((m) => m.poster);

// Shuffle once at module load — fresh order per page load, stable per render
function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

const IMAGES = shuffle(ALL_IMAGES);
const INTERVAL_MS = 5500;

export function HeroBackgroundSlideshow() {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent((prev) => (prev + 1) % IMAGES.length);
    }, INTERVAL_MS);
    return () => clearInterval(timer);
  }, []);

  return (
    <div
      aria-hidden="true"
      style={{
        position: 'absolute',
        inset: 0,
        zIndex: 0,
        overflow: 'hidden',
        backgroundColor: '#0B0B0F',
      }}
    >
      {/* All images stacked — only the active one is visible via opacity */}
      {IMAGES.map((src, i) => (
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
            // Ken Burns: the active image slowly zooms in via CSS animation
            animation: i === current ? `kenBurns ${INTERVAL_MS}ms ease-in-out forwards` : 'none',
            transition: `opacity 1.5s ease-in-out`,
            filter: 'saturate(0.7)',
            willChange: 'opacity, transform',
          }}
        />
      ))}

      {/* Dark overlay for text readability */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.58)',
        }}
      />

      {/* Cinematic vignette */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'radial-gradient(ellipse at center, transparent 35%, rgba(0,0,0,0.5) 100%)',
        }}
      />

      {/* Bottom fade into page */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          bottom: 0,
          height: '200px',
          background: 'linear-gradient(to top, #0B0B0F, transparent)',
        }}
      />

      {/* CSS keyframe for Ken Burns effect */}
      <style>{`
        @keyframes kenBurns {
          from { transform: scale(1.0) translate(0, 0); }
          to   { transform: scale(1.08) translate(-1%, -0.5%); }
        }
      `}</style>
    </div>
  );
}
