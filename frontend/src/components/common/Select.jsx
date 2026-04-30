import './Input.css';
import './Select.css';

export default function Select({
  label,
  error,
  hint,
  id,
  required,
  options = [],
  placeholder,
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
      <select
        id={id}
        className={`input-field select-field ${error ? 'input-field--error' : ''}`}
        {...rest}
      >
        {placeholder && <option value="">{placeholder}</option>}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <span className="input-error-text">{error}</span>}
    </div>
  );
}
