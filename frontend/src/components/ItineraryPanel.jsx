export default function ItineraryPanel({ plan, loading, onGenerate, onClose }) {
  if (loading) {
    return (
      <section className="itinerary-panel">
        <p className="eyebrow">Day-by-day plan</p>
        <p className="lede">Building your itinerary…</p>
      </section>
    )
  }

  if (!plan) {
    return (
      <section className="itinerary-panel">
        <p className="eyebrow">Day-by-day plan</p>
        <h3>Turn this match into a usable trip</h3>
        <p className="lede">Get a paced itinerary, packing tips, and live concierge swaps for rain or crowds.</p>
        <button type="button" className="primary-btn" onClick={onGenerate}>
          Generate itinerary
        </button>
      </section>
    )
  }

  return (
    <section className="itinerary-panel">
      <header className="itinerary-header">
        <div>
          <p className="eyebrow">Day-by-day plan · {plan.source === 'groq' ? 'AI' : 'Smart template'}</p>
          <h3>{plan.destination_name}</h3>
          <p className="lede">{plan.summary}</p>
        </div>
        <div className="itinerary-actions">
          <button type="button" className="ghost-btn" onClick={onGenerate}>
            Regenerate
          </button>
          {onClose && (
            <button type="button" className="ghost-btn" onClick={onClose}>
              Close
            </button>
          )}
        </div>
      </header>

      <div className="itinerary-days">
        {plan.days.map((day) => (
          <article key={day.day} className="day-card">
            <h4>
              Day {day.day}
              <span>{day.title?.replace(/^Day\s+\d+:\s*/i, '') || day.focus}</span>
            </h4>
            <p className="day-focus">{day.focus}</p>
            <ul>
              {(day.activities || []).map((a, idx) => (
                <li key={`${day.day}-${idx}`}>
                  <strong>{a.time}</strong>
                  <span>{a.title}</span>
                  <em>{a.note}</em>
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>

      <div className="itinerary-side">
        <div>
          <h4>AI Concierge</h4>
          <ul className="concierge-list">
            {(plan.concierge || []).map((c) => (
              <li key={c.trigger}>
                <strong>{c.trigger}</strong>
                <span>{c.action}</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Packing tips</h4>
          <ul className="pack-list">
            {(plan.packing_tips || []).map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
