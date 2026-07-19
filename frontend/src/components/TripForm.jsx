import { formatInr } from '../defaults'

const STYLES = [
  'Nature',
  'Cafes',
  'Photography',
  'History',
  'Relaxation',
  'Nightlife',
  'Trekking',
  'Beach',
  'Mountains',
  'Museums',
  'Architecture',
]

const AVOID = ['Crowds', 'Nightlife', 'Trekking', 'Expensive food', 'Shopping']

function Chip({ active, onClick, children }) {
  return (
    <button type="button" className={`chip ${active ? 'active' : ''}`} onClick={onClick}>
      {children}
    </button>
  )
}

export default function TripForm({ prefs, setPrefs, meta, onSubmit, loading }) {
  const cities = meta?.starting_cities?.length
    ? meta.starting_cities
    : ['Delhi', 'Mumbai', 'Bangalore', 'London', 'New York', 'Singapore', 'Dubai']
  const passports = meta?.passports || ['Indian', 'US', 'UK', 'EU', 'Singapore']

  function toggle(listKey, value) {
    setPrefs((p) => {
      const list = p[listKey]
      return {
        ...p,
        [listKey]: list.includes(value) ? list.filter((v) => v !== value) : [...list, value],
      }
    })
  }

  return (
    <form
      className="trip-form"
      onSubmit={(e) => {
        e.preventDefault()
        onSubmit()
      }}
    >
      <header className="form-header">
        <p className="eyebrow">Step 1</p>
        <h2>Tell us about your ideal trip.</h2>
        <p className="lede">Destination is the output. Constraints and feelings are the input.</p>
      </header>

      <div className="field-grid">
        <label className="field">
          <span>Budget</span>
          <div className="slider-row">
            <input
              type="range"
              min={10000}
              max={200000}
              step={2500}
              value={prefs.budget_inr}
              onChange={(e) => setPrefs((p) => ({ ...p, budget_inr: Number(e.target.value) }))}
            />
            <strong>{formatInr(prefs.budget_inr)}</strong>
          </div>
        </label>

        <label className="field">
          <span>Days</span>
          <div className="slider-row">
            <input
              type="range"
              min={2}
              max={21}
              value={prefs.days}
              onChange={(e) => setPrefs((p) => ({ ...p, days: Number(e.target.value) }))}
            />
            <strong>{prefs.days}</strong>
          </div>
        </label>

        <label className="field">
          <span>Starting city</span>
          <select
            value={prefs.starting_city}
            onChange={(e) => setPrefs((p) => ({ ...p, starting_city: e.target.value }))}
          >
            {cities.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Passport</span>
          <select
            value={prefs.passport}
            onChange={(e) => setPrefs((p) => ({ ...p, passport: e.target.value }))}
          >
            {passports.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
      </div>

      <fieldset className="chip-fieldset">
        <legend>Travel style</legend>
        <div className="chip-row">
          {STYLES.map((s) => (
            <Chip key={s} active={prefs.travel_styles.includes(s)} onClick={() => toggle('travel_styles', s)}>
              {s}
            </Chip>
          ))}
        </div>
      </fieldset>

      <fieldset className="chip-fieldset">
        <legend>Avoid</legend>
        <div className="chip-row">
          {AVOID.map((s) => (
            <Chip key={s} active={prefs.avoid.includes(s)} onClick={() => toggle('avoid', s)}>
              {s}
            </Chip>
          ))}
        </div>
      </fieldset>

      <div className="field-grid">
        <label className="field">
          <span>Pace</span>
          <select value={prefs.pace} onChange={(e) => setPrefs((p) => ({ ...p, pace: e.target.value }))}>
            <option value="slow">Slow</option>
            <option value="moderate">Moderate</option>
            <option value="fast">Fast</option>
          </select>
        </label>

        <label className="field">
          <span>Travel companion</span>
          <select
            value={prefs.companion}
            onChange={(e) => setPrefs((p) => ({ ...p, companion: e.target.value }))}
          >
            <option value="solo">Solo</option>
            <option value="friends">Friends</option>
            <option value="family">Family</option>
            <option value="partner">Partner</option>
          </select>
        </label>

        <label className="field">
          <span>Weather min °C</span>
          <input
            type="number"
            value={prefs.weather_min_c}
            onChange={(e) => setPrefs((p) => ({ ...p, weather_min_c: Number(e.target.value) }))}
          />
        </label>

        <label className="field">
          <span>Weather max °C</span>
          <input
            type="number"
            value={prefs.weather_max_c}
            onChange={(e) => setPrefs((p) => ({ ...p, weather_max_c: Number(e.target.value) }))}
          />
        </label>

        <label className="field full">
          <span>Max flight hours</span>
          <div className="slider-row">
            <input
              type="range"
              min={2}
              max={24}
              step={0.5}
              value={prefs.max_flight_hours}
              onChange={(e) => setPrefs((p) => ({ ...p, max_flight_hours: Number(e.target.value) }))}
            />
            <strong>{prefs.max_flight_hours}h</strong>
          </div>
        </label>
      </div>

      <label className="field full experience">
        <span>Experience search (optional)</span>
        <input
          type="text"
          placeholder='e.g. "Somewhere like Kyoto but less crowded"'
          value={prefs.experience_query}
          onChange={(e) => setPrefs((p) => ({ ...p, experience_query: e.target.value }))}
        />
      </label>

      <button className="primary-btn" type="submit" disabled={loading}>
        {loading ? 'Matching destinations…' : 'Find my destinations'}
      </button>
    </form>
  )
}
