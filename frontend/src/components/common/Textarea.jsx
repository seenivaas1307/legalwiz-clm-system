import './Input.css';

export default function Textarea({
  label,
  error,
  hint,
  id,
  required,
  rows = 4,
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
      <textarea
        id={id}
        rows={rows}
        className={`input-field textarea-field ${error ? 'input-field--error' : ''}`}
        {...rest}
      />
      {error && <span className="input-error-text">{error}</span>}
    </div>
  );
}
