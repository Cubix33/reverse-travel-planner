import { formatInr } from '../defaults'

export default function WhatIf({ prefs, setPrefs, onRecalculate, loading }) {
  return (
    <section className="what-if">
      <div className="what-if-copy">
        <p className="eyebrow">What If mode</p>
        <h3>Move the constraints. Watch destinations rearrange.</h3>
      </div>
      <div className="what-if-controls">
        <label>
          <span>Budget {formatInr(prefs.budget_inr)}</span>
          <input
            type="range"
            min={10000}
            max={200000}
            step={2500}
            value={prefs.budget_inr}
            onChange={(e) => {
              const budget_inr = Number(e.target.value)
              setPrefs((p) => ({ ...p, budget_inr }))
              onRecalculate({ ...prefs, budget_inr })
            }}
          />
        </label>
        <label>
          <span>Days {prefs.days}</span>
          <input
            type="range"
            min={2}
            max={21}
            value={prefs.days}
            onChange={(e) => {
              const days = Number(e.target.value)
              setPrefs((p) => ({ ...p, days }))
              onRecalculate({ ...prefs, days })
            }}
          />
        </label>
        <label>
          <span>Max flight {prefs.max_flight_hours}h</span>
          <input
            type="range"
            min={2}
            max={24}
            step={0.5}
            value={prefs.max_flight_hours}
            onChange={(e) => {
              const max_flight_hours = Number(e.target.value)
              setPrefs((p) => ({ ...p, max_flight_hours }))
              onRecalculate({ ...prefs, max_flight_hours })
            }}
          />
        </label>
      </div>
      {loading && <p className="live-hint">Recalculating live…</p>}
    </section>
  )
}
