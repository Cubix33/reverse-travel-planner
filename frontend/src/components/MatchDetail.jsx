import { formatInr } from '../defaults'

export default function MatchDetail({
  match,
  explanation,
  explaining,
  onExplain,
  onGenerateItinerary,
  onSave,
  saved,
  compareSelected,
  onToggleCompare,
  itineraryLoading,
}) {
  if (!match) {
    return (
      <aside className="detail-panel empty">
        <p>Select a destination to see why it matched — dimensions, genome, budget split, and next actions.</p>
      </aside>
    )
  }

  const genomeEntries = Object.entries(match.genome_highlights || {})

  return (
    <aside className="detail-panel">
      <header>
        <p className="eyebrow">Why this place</p>
        <h3>
          {match.name}
          <span>
            {match.country} · {match.match_percent}% match
          </span>
        </h3>
        <p className="tagline">{match.tagline}</p>
        <div className="detail-actions">
          <button type="button" className="ghost-btn" onClick={onSave}>
            {saved ? 'Saved' : 'Save trip'}
          </button>
          <button
            type="button"
            className={`ghost-btn ${compareSelected ? 'active-toggle' : ''}`}
            onClick={onToggleCompare}
          >
            {compareSelected ? 'In compare' : 'Add to compare'}
          </button>
          <button type="button" className="primary-btn inline" onClick={onGenerateItinerary} disabled={itineraryLoading}>
            {itineraryLoading ? 'Building…' : 'Build itinerary'}
          </button>
        </div>
      </header>

      <section className="dimensions">
        <h4>Match dimensions</h4>
        {match.dimensions.map((d) => (
          <div key={d.label} className="dim-row">
            <div className="dim-label">
              <span>{d.label}</span>
              <strong>{d.score}%</strong>
            </div>
            <div className="dim-track">
              <div className="dim-fill" style={{ width: `${d.score}%` }} />
            </div>
          </div>
        ))}
      </section>

      {!!genomeEntries.length && (
        <section className="genome-box">
          <h4>Destination genome</h4>
          <div className="genome-grid">
            {genomeEntries.map(([k, v]) => (
              <div key={k} className="genome-chip">
                <span>{k.replace('_', ' ')}</span>
                <strong>{v}</strong>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="reasons">
        <h4>Explainability</h4>
        <ul>
          {match.reasons.positive.map((r) => (
            <li key={r} className="pos">
              {r}
            </li>
          ))}
          {match.reasons.negative.map((r) => (
            <li key={r} className="neg">
              {r}
            </li>
          ))}
        </ul>
        <button type="button" className="ghost-btn" onClick={onExplain} disabled={explaining}>
          {explaining ? 'Writing explanation…' : explanation ? 'Refresh AI explanation' : 'Generate AI explanation'}
        </button>
        {explanation && <pre className="ai-explain">{explanation}</pre>}
      </section>

      <section className="budget-box">
        <h4>Smart budget allocation</h4>
        <p className="total">{formatInr(match.estimated_total_inr)} estimated total</p>
        <ul>
          {Object.entries(match.budget_breakdown)
            .filter(([k]) => k !== 'per_day')
            .map(([k, v]) => (
              <li key={k}>
                <span>{k}</span>
                <strong>{formatInr(v)}</strong>
              </li>
            ))}
        </ul>
      </section>

      <section className="gems">
        <h4>Hidden gems</h4>
        <ul>
          {match.hidden_gems.map((g) => (
            <li key={g}>{g}</li>
          ))}
        </ul>
      </section>
    </aside>
  )
}
