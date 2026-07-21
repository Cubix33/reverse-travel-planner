import { twinInsights } from '../storage'
import { formatInr } from '../defaults'

function topEntries(obj, n = 4) {
  return Object.entries(obj || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
}

export default function TravelTwin({ twin }) {
  const insights = twinInsights(twin)
  const styles = topEntries(twin.preferredStyles)
  const avoids = topEntries(twin.avoided)

  return (
    <section className="travel-twin">
      <div>
        <p className="eyebrow">Travel Twin</p>
        <h2>Your profile gets sharper every trip</h2>
        <p className="lede">
          Persistent learning from searches, saves, and preferences — so recommendations stop starting from
          scratch.
        </p>
      </div>

      <div className="twin-stats">
        <div>
          <strong>{twin.tripsLogged}</strong>
          <span>searches logged</span>
        </div>
        <div>
          <strong>{twin.avgBudget ? formatInr(twin.avgBudget) : '—'}</strong>
          <span>typical budget</span>
        </div>
        <div>
          <strong>{twin.avgDays || '—'}</strong>
          <span>avg days</span>
        </div>
        <div>
          <strong>{twin.savedDestinationIds?.length || 0}</strong>
          <span>destinations touched</span>
        </div>
      </div>

      <div className="twin-columns">
        <div>
          <h4>Learned leanings</h4>
          <ul>
            {insights.map((n) => (
              <li key={n}>{n}</li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Styles you repeat</h4>
          {styles.length ? (
            <ul>
              {styles.map(([k, v]) => (
                <li key={k}>
                  {k} <em>×{v}</em>
                </li>
              ))}
            </ul>
          ) : (
            <p className="lede">Run a few searches to train this.</p>
          )}
          <h4>Things you avoid</h4>
          {avoids.length ? (
            <ul>
              {avoids.map(([k, v]) => (
                <li key={k}>
                  {k} <em>×{v}</em>
                </li>
              ))}
            </ul>
          ) : (
            <p className="lede">No strong avoid signals yet.</p>
          )}
        </div>
      </div>
    </section>
  )
}
