/**
 * ContractStepper
 *
 * A "soft" horizontal stepper — all steps are clickable, recommended order.
 * Steps can be marked done (✓) or active (highlighted ring + scale).
 *
 * Props:
 *   steps       — array of { key, label, icon: LucideComponent }
 *   activeStep  — string key of the currently active step
 *   doneSteps   — Set<string> of completed step keys
 *   onStepClick — (key: string) => void — called on back/forward or step node click
 *   children    — content to render inside the active step pane
 *   showNav     — bool (default true) — show bottom Prev/Next navigation
 *   onNext      — () => void — called when Next is clicked
 *   onPrev      — () => void — called when Prev is clicked
 *   nextLabel   — string (default "Next")
 *   prevLabel   — string (default "Back")
 *   nextDisabled — bool
 *   nextLoading  — bool
 */

import { Check, ChevronLeft, ChevronRight } from 'lucide-react';
import Button from '../common/Button.jsx';
import './ContractStepper.css';

export default function ContractStepper({
  steps = [],
  activeStep,
  doneSteps = new Set(),
  onStepClick,
  children,
  showNav = true,
  onNext,
  onPrev,
  nextLabel = 'Next',
  prevLabel = 'Back',
  nextDisabled = false,
  nextLoading = false,
}) {
  const currentIndex = steps.findIndex((s) => s.key === activeStep);
  const isFirst = currentIndex === 0;
  const isLast = currentIndex === steps.length - 1;

  // Progress = steps before the current one + 1 completed === ratio of done
  const progressPct = steps.length > 1
    ? Math.round((currentIndex / (steps.length - 1)) * 100)
    : 0;

  return (
    <div className="stepper">

      {/* ── Step rail ───────────────────────────────────────────────── */}
      <div className="stepper__rail" role="navigation" aria-label="Contract workflow steps">
        {steps.map((step) => {
          const isDone = doneSteps.has(step.key);
          const isActive = step.key === activeStep;
          const Icon = step.icon;
          const stepClass = [
            'stepper__step',
            isActive ? 'stepper__step--active' : '',
            isDone   ? 'stepper__step--done'   : '',
          ].filter(Boolean).join(' ');

          return (
            <button
              key={step.key}
              className={stepClass}
              onClick={() => onStepClick?.(step.key)}
              aria-current={isActive ? 'step' : undefined}
              aria-label={`${step.label}${isDone ? ' (completed)' : ''}`}
              type="button"
            >
              <div className="stepper__node">
                {isDone && !isActive ? (
                  <Check size={14} strokeWidth={3} />
                ) : (
                  <Icon size={14} strokeWidth={2} />
                )}
              </div>
              <span className="stepper__label">{step.label}</span>
            </button>
          );
        })}
      </div>

      {/* ── Progress bar ────────────────────────────────────────────── */}
      <div className="stepper__progress" role="progressbar" aria-valuenow={progressPct} aria-valuemin={0} aria-valuemax={100}>
        <div className="stepper__progress-fill" style={{ width: `${progressPct}%` }} />
      </div>

      {/* ── Content pane ────────────────────────────────────────────── */}
      {/* key forces re-mount + re-animation on step change */}
      <div className="stepper__content" key={activeStep}>
        {children}
      </div>

      {/* ── Navigation row ──────────────────────────────────────────── */}
      {showNav && (
        <div className="stepper__nav">
          <div className="stepper__nav-left">
            {!isFirst && (
              <Button
                variant="ghost"
                size="sm"
                icon={ChevronLeft}
                onClick={onPrev}
                type="button"
              >
                {prevLabel}
              </Button>
            )}
          </div>

          <span className="stepper__counter">
            Step {currentIndex + 1} of {steps.length}
          </span>

          <div className="stepper__nav-right">
            <Button
              variant={isLast ? 'primary' : 'secondary'}
              size="sm"
              icon={isLast ? undefined : ChevronRight}
              onClick={onNext}
              disabled={nextDisabled}
              loading={nextLoading}
              type="button"
            >
              {isLast ? 'Finish' : nextLabel}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
