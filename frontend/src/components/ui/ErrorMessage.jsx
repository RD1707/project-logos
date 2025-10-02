import { AlertCircle, XCircle } from 'lucide-react';
import clsx from 'clsx';

export default function ErrorMessage({
  title = 'Erro',
  message,
  variant = 'error',
  onDismiss,
  className
}) {
  const variants = {
    error: {
      container: 'bg-red-50 border-red-200',
      icon: 'text-red-600',
      title: 'text-red-800',
      message: 'text-red-700',
      Icon: AlertCircle,
    },
    warning: {
      container: 'bg-yellow-50 border-yellow-200',
      icon: 'text-yellow-600',
      title: 'text-yellow-800',
      message: 'text-yellow-700',
      Icon: AlertCircle,
    },
    info: {
      container: 'bg-blue-50 border-blue-200',
      icon: 'text-blue-600',
      title: 'text-blue-800',
      message: 'text-blue-700',
      Icon: AlertCircle,
    },
  };

  const config = variants[variant];
  const Icon = config.Icon;

  return (
    <div
      className={clsx(
        'rounded-lg border p-4',
        config.container,
        className
      )}
    >
      <div className="flex items-start gap-3">
        <Icon className={clsx('h-5 w-5 flex-shrink-0 mt-0.5', config.icon)} />

        <div className="flex-1">
          <h3 className={clsx('font-semibold text-sm', config.title)}>
            {title}
          </h3>
          {message && (
            <p className={clsx('mt-1 text-sm', config.message)}>
              {message}
            </p>
          )}
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className={clsx('flex-shrink-0 transition-colors', config.icon)}
          >
            <XCircle className="h-5 w-5" />
          </button>
        )}
      </div>
    </div>
  );
}
