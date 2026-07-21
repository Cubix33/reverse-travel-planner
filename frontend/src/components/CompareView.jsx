import { formatInr } from '../defaults'

const GENOME_KEYS = [
  'nature',
  'cafes',
  'photography',
  'history',
  'relaxation',
  'crowds',
  'walkability',
  'internet',
  'safety',
  'beach',
  'mountains',
]

export default function CompareView({ data, onClose }) {
  if (!data?.items?.length) return null
  const items = data.items

  return (
    <section className="compare-view">
      <header>
        <div>
          <p className="eyebrow">Compare</p>
          <h3>
            Side-by-side matchup
            <span>Current edge: {data.winner}</span>
          </h3>
        </div>
        <button type="button" className="ghost-btn" onClick={onClose}>
          Close compare
        </button>
      </header>

      <div className="compare-scroll">
        <table className="compare-table">
          <thead>
            <tr>
              <th>Metric</th>
              {items.map((item) => (
                <th key={item.match.id}>
                  <strong>{item.match.name}</strong>
                  <span>
                    {item.match.country} · {item.match.match_percent}%
                  </span>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Est. total</td>
              {items.map((item) => (
                <td key={`${item.match.id}-cost`}>{formatInr(item.match.estimated_total_inr)}</td>
              ))}
            </tr>
            <tr>
              <td>Flight</td>
              {items.map((item) => (
                <td key={`${item.match.id}-flight`}>{item.match.flight_hours}h</td>
              ))}
            </tr>
            <tr>
              <td>Weather</td>
              {items.map((item) => (
                <td key={`${item.match.id}-temp`}>{item.match.avg_temp_c}°C</td>
              ))}
            </tr>
            <tr>
              <td>Visa</td>
              {items.map((item) => (
                <td key={`${item.match.id}-visa`}>{item.match.visa_status}</td>
              ))}
            </tr>
            {GENOME_KEYS.map((key) => (
              <tr key={key}>
                <td>{key.replace('_', ' ')}</td>
                {items.map((item) => {
                  const score = item.genome?.[key] ?? 0
                  return (
                    <td key={`${item.match.id}-${key}`}>
                      <div className="compare-meter">
                        <div className="dim-track">
                          <div className="dim-fill" style={{ width: `${score}%` }} />
                        </div>
                        <span>{score}</span>
                      </div>
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}
