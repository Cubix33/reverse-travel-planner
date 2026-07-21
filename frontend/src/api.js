const BASE = ''

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Request failed: ${res.status}`)
  }
  return res.json()
}

export function fetchMeta() {
  return request('/api/meta')
}

export function recommend(preferences, limit = 8) {
  return request(`/api/recommend?limit=${limit}`, {
    method: 'POST',
    body: JSON.stringify(preferences),
  })
}

export function explain(destinationId, preferences) {
  return request('/api/explain', {
    method: 'POST',
    body: JSON.stringify({ destination_id: destinationId, preferences }),
  })
}

export function experienceSearch(payload) {
  return request('/api/experience-search', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function fetchItinerary(destinationId, preferences) {
  return request('/api/itinerary', {
    method: 'POST',
    body: JSON.stringify({ destination_id: destinationId, preferences }),
  })
}

export function compareDestinations(destinationIds, preferences) {
  return request('/api/compare', {
    method: 'POST',
    body: JSON.stringify({ destination_ids: destinationIds, preferences }),
  })
}

export function fetchDestination(id) {
  return request(`/api/destinations/${id}`)
}
