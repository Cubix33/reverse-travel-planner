import { formatInr } from '../defaults'

export default function SavedTrips({ trips, onOpen, onRemove }) {
  return (
    <section className="saved-trips">
      <header>
        <p className="eyebrow">Saved trips</p>
        <h2>Pick up where you left off</h2>
      </header>
      {!trips.length ? (
        <p className="lede">Save a match from results to keep shortlists and reopen them later.</p>
      ) : (
        <div className="saved-grid">
          {trips.map((trip) => (
            <article key={trip.id} className="saved-card">
              <div>
                <h3>
                  {trip.destinationName}
                  <span>{trip.destinationCountry}</span>
                </h3>
                <p>
                  {trip.days} days · {formatInr(trip.budgetInr)} · {trip.matchPercent}% match
                </p>
              </div>
              <div className="saved-actions">
                <button type="button" className="ghost-btn" onClick={() => onOpen(trip)}>
                  Reopen
                </button>
                <button type="button" className="ghost-btn danger" onClick={() => onRemove(trip.id)}>
                  Remove
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
