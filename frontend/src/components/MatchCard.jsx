import { formatInr } from '../defaults'

export default function MatchCard({ match, rank, selected, onSelect, compareSelected, onToggleCompare }) {
  return (
    <div className={`match-card ${selected ? 'selected' : ''}`} style={{ animationDelay: `${rank * 70}ms` }}>
      <button type="button" className="match-card-main" onClick={() => onSelect(match)}>
        <div className="match-rank">#{rank}</div>
        <div className="match-main">
          <h3>
            {match.name}
            <span>{match.country}</span>
          </h3>
          <p>{match.tagline}</p>
          <div className="match-meta">
            <span>{formatInr(match.estimated_total_inr)}</span>
            <span>{match.flight_hours}h flight</span>
            <span>{match.avg_temp_c}°C</span>
          </div>
        </div>
        <div className="match-score" aria-label={`${match.match_percent} percent match`}>
          <svg viewBox="0 0 36 36" className="ring">
            <path
              className="ring-bg"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              className="ring-fg"
              strokeDasharray={`${match.match_percent}, 100`}
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
          </svg>
          <strong>{match.match_percent}%</strong>
        </div>
      </button>
      <button
        type="button"
        className={`compare-toggle ${compareSelected ? 'on' : ''}`}
        onClick={() => onToggleCompare(match)}
        aria-pressed={compareSelected}
      >
        {compareSelected ? 'Comparing' : 'Compare'}
      </button>
    </div>
  )
}
