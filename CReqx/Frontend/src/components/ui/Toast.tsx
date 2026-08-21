import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { CheckCircle2, XCircle, Info, X } from 'lucide-react';
import { cn } from '../../lib/utils';

type ToastType = 'success' | 'error' | 'info';

interface ToastItem {
  id: number;
  message: string;
  type: ToastType;
}

let _push: ((msg: string, type?: ToastType) => void) | null = null;

export function toast(message: string, type: ToastType = 'success') {
  _push?.(message, type);
}

const icons = {
  success: CheckCircle2,
  error: XCircle,
  info: Info,
};

const styles = {
  success: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
  error: 'border-ember-500/30 bg-ember-500/10 text-ember-300',
  info: 'border-dusk-400/30 bg-dusk-400/10 text-dusk-300',
};

function ToastItem({ item, onDismiss }: { item: ToastItem; onDismiss: () => void }) {
  const Icon = icons[item.type];
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    timerRef.current = setTimeout(onDismiss, 3500);
    return () => clearTimeout(timerRef.current);
  }, [onDismiss]);

  return (
    <div
      className={cn(
        'flex items-center gap-3 rounded-xl border px-4 py-3 shadow-2xl shadow-black/40 text-sm font-medium backdrop-blur-md',
        'animate-in slide-in-from-bottom-4 duration-300',
        styles[item.type]
      )}
    >
      <Icon className="h-4 w-4 shrink-0" />
      <span className="flex-1">{item.message}</span>
      <button onClick={onDismiss} className="ml-2 opacity-60 hover:opacity-100 transition-opacity">
        <X className="h-3.5 w-3.5" />
      </button>
    </div>
  );
}

export function ToastHost() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);
  const counterRef = useRef(0);

  useEffect(() => {
    _push = (message, type = 'success') => {
      const id = ++counterRef.current;
      setToasts((prev) => [...prev, { id, message, type }]);
    };
    return () => { _push = null; };
  }, []);

  const dismiss = (id: number) => setToasts((prev) => prev.filter((t) => t.id !== id));

  if (!toasts.length) return null;

  return createPortal(
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-2 max-w-sm w-full">
      {toasts.map((t) => (
        <ToastItem key={t.id} item={t} onDismiss={() => dismiss(t.id)} />
      ))}
    </div>,
    document.body
  );
}