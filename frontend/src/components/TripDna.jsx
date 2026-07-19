export default function TripDna({ dna }) {
  if (!dna) return null
  const entries = Object.entries(dna).sort((a, b) => b[1] - a[1])

  return (
    <section className="trip-dna">
      <div>
        <p className="eyebrow">Trip DNA</p>
        <h3>Your traveler profile for this search</h3>
      </div>
      <div className="dna-grid">
        {entries.map(([label, score]) => (
          <div key={label} className="dna-item">
            <div className="dna-top">
              <span>{label}</span>
              <strong>{score}%</strong>
            </div>
            <div className="dim-track">
              <div className="dim-fill dna" style={{ width: `${score}%` }} />
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
