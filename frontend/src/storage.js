const TWIN_KEY = 'rtp_travel_twin_v1'
const SAVED_KEY = 'rtp_saved_trips_v1'

const EMPTY_TWIN = {
  tripsLogged: 0,
  preferredStyles: {},
  avoided: {},
  companions: {},
  paces: {},
  avgBudget: 0,
  avgDays: 0,
  savedDestinationIds: [],
  notes: [],
}

export function loadTwin() {
  try {
    return { ...EMPTY_TWIN, ...JSON.parse(localStorage.getItem(TWIN_KEY) || '{}') }
  } catch {
    return { ...EMPTY_TWIN }
  }
}

export function saveTwin(twin) {
  localStorage.setItem(TWIN_KEY, JSON.stringify(twin))
}

export function updateTwinFromSearch(prefs, matches = []) {
  const twin = loadTwin()
  twin.tripsLogged += 1
  twin.avgBudget = Math.round((twin.avgBudget * (twin.tripsLogged - 1) + prefs.budget_inr) / twin.tripsLogged)
  twin.avgDays = Math.round((twin.avgDays * (twin.tripsLogged - 1) + prefs.days) / twin.tripsLogged)

  for (const style of prefs.travel_styles || []) {
    twin.preferredStyles[style] = (twin.preferredStyles[style] || 0) + 1
  }
  for (const a of prefs.avoid || []) {
    twin.avoided[a] = (twin.avoided[a] || 0) + 1
  }
  twin.companions[prefs.companion] = (twin.companions[prefs.companion] || 0) + 1
  twin.paces[prefs.pace] = (twin.paces[prefs.pace] || 0) + 1

  for (const m of matches.slice(0, 3)) {
    if (!twin.savedDestinationIds.includes(m.id)) {
      twin.savedDestinationIds.push(m.id)
    }
  }
  twin.savedDestinationIds = twin.savedDestinationIds.slice(-20)

  const topStyle = Object.entries(twin.preferredStyles).sort((a, b) => b[1] - a[1])[0]?.[0]
  if (topStyle) {
    twin.notes = [
      `You consistently lean toward ${topStyle.toLowerCase()} trips.`,
      twin.avoided.Crowds ? 'You usually prefer lower-crowd destinations.' : 'Crowd sensitivity is still forming.',
      twin.avgBudget
        ? `Typical budget settles near ₹${twin.avgBudget.toLocaleString('en-IN')} for ~${twin.avgDays} days.`
        : 'Budget pattern still learning.',
    ]
  }

  saveTwin(twin)
  return twin
}

export function loadSavedTrips() {
  try {
    return JSON.parse(localStorage.getItem(SAVED_KEY) || '[]')
  } catch {
    return []
  }
}

export function saveTrip(trip) {
  const all = loadSavedTrips()
  const next = [{ ...trip, id: trip.id || `trip_${Date.now()}`, savedAt: Date.now() }, ...all].slice(0, 20)
  localStorage.setItem(SAVED_KEY, JSON.stringify(next))
  return next
}

export function removeSavedTrip(id) {
  const next = loadSavedTrips().filter((t) => t.id !== id)
  localStorage.setItem(SAVED_KEY, JSON.stringify(next))
  return next
}

export function twinInsights(twin) {
  if (!twin.tripsLogged) {
    return [
      'Travel Twin learns from every search you run.',
      'After a few trips it will spot patterns like mountains over beaches.',
      'Saved destinations also feed your long-term profile.',
    ]
  }
  return twin.notes?.length
    ? twin.notes
    : [`${twin.tripsLogged} searches logged — profile is warming up.`]
}
