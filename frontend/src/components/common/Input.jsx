import './Input.css';

export default function Input({
  label,
  error,
  hint,
  id,
  required,
  className = '',
  ...rest
}) {
  return (
    <div className={`input-group ${className}`}>
      {label && (
        <label htmlFor={id} className="input-label">
          {label}
          {required && <span className="input-required" aria-hidden="true">*</span>}
        </label>
      )}
      {hint && <span className="input-hint">{hint}</span>}
      <input
        id={id}
        className={`input-field ${error ? 'input-field--error' : ''}`}
        {...rest}
      />
      {error && <span className="input-error-text">{error}</span>}
    </div>
  );
}
