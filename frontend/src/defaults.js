export const DEFAULT_PREFS = {
  budget_inr: 40000,
  days: 5,
  starting_city: 'Delhi',
  passport: 'Indian',
  travel_styles: ['Nature', 'Cafes', 'Photography'],
  avoid: ['Crowds'],
  pace: 'slow',
  weather_min_c: 15,
  weather_max_c: 28,
  companion: 'solo',
  max_flight_hours: 6,
  experience_query: '',
}

export function formatInr(n) {
  return `₹${Number(n).toLocaleString('en-IN')}`
}
