import { AlertTriangle, SearchX, Star } from 'lucide-react';
import { Link } from 'react-router-dom';

export function ErrorState({ message = 'Something went wrong.' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center gap-4 py-16 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-ember-500/10">
        <AlertTriangle className="h-8 w-8 text-ember-400" />
      </div>
      <h3 className="font-display text-lg font-semibold text-mist-100">Oops!</h3>
      <p className="max-w-xs text-sm text-mist-400">{message}</p>
      <Link
        to="/"
        className="rounded-full bg-ember-500 px-5 py-2 text-sm font-semibold text-white"
      >
        Back to home
      </Link>
    </div>
  );
}

export function EmptyState({
  icon: Icon = SearchX,
  title = 'Nothing here yet',
  description = '',
  action,
}: {
  icon?: React.ElementType;
  title?: string;
  description?: string;
  action?: { label: string; to: string };
}) {
  return (
    <div className="flex flex-col items-center gap-4 py-16 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-void-800">
        <Icon className="h-8 w-8 text-mist-500" />
      </div>
      <h3 className="font-display text-lg font-semibold text-mist-200">{title}</h3>
      {description && <p className="max-w-xs text-sm text-mist-400">{description}</p>}
      {action && (
        <Link
          to={action.to}
          className="rounded-full bg-ember-500 px-5 py-2 text-sm font-semibold text-white"
        >
          {action.label}
        </Link>
      )}
    </div>
  );
}
