import { useState } from 'react'

const FALLBACK_EXAMPLES = [
  'Somewhere like Switzerland but cheaper',
  'Somewhere like Kyoto but less crowded',
  'A place where I can read books in cafés all day',
  'Quiet mountains with good Wi-Fi for remote work',
]

export default function ExperienceSearch({ examples, prefs, onSearch, loading }) {
  const [query, setQuery] = useState('')
  const chips = examples?.length ? examples : FALLBACK_EXAMPLES

  return (
    <section className="experience-search">
      <p className="eyebrow">Experience search</p>
      <h3>Search by feeling, not country</h3>
      <form
        onSubmit={(e) => {
          e.preventDefault()
          if (query.trim()) onSearch(query.trim())
        }}
      >
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder='e.g. "I want autumn in a walkable town"'
        />
        <button type="submit" className="primary-btn" disabled={loading || !query.trim()}>
          {loading ? 'Searching…' : 'Search experiences'}
        </button>
      </form>
      <div className="chip-row">
        {chips.map((ex) => (
          <button
            key={ex}
            type="button"
            className="chip"
            onClick={() => {
              setQuery(ex)
              onSearch(ex)
            }}
          >
            {ex}
          </button>
        ))}
      </div>
      <p className="hint">
        Uses your current hub ({prefs.starting_city}), budget, and passport as soft constraints.
      </p>
    </section>
  )
}
