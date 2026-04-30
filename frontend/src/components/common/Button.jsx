import './Button.css';

export default function Button({
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon: Icon,
  children,
  className = '',
  ...rest
}) {
  return (
    <button
      className={`btn btn--${variant} btn--${size} ${loading ? 'btn--loading' : ''} ${className}`}
      disabled={disabled || loading}
      {...rest}
    >
      {Icon && !loading && <Icon size={size === 'sm' ? 14 : 16} strokeWidth={1.75} />}
      {loading && <span className="btn__spinner" />}
      {children}
    </button>
  );
}
