import { useEffect, useRef, useState } from 'react'
import {
  compareDestinations,
  explain,
  experienceSearch,
  fetchItinerary,
  fetchMeta,
  recommend,
} from './api'
import { DEFAULT_PREFS } from './defaults'
import CompareView from './components/CompareView'
import ExperienceSearch from './components/ExperienceSearch'
import ItineraryPanel from './components/ItineraryPanel'
import MatchCard from './components/MatchCard'
import MatchDetail from './components/MatchDetail'
import SavedTrips from './components/SavedTrips'
import TravelTwin from './components/TravelTwin'
import TripDna from './components/TripDna'
import TripForm from './components/TripForm'
import WhatIf from './components/WhatIf'
import {
  loadSavedTrips,
  loadTwin,
  removeSavedTrip,
  saveTrip,
  updateTwinFromSearch,
} from './storage'
import './App.css'

export default function App() {
  const [stage, setStage] = useState('hero')
  const [prefs, setPrefs] = useState(DEFAULT_PREFS)
  const [meta, setMeta] = useState(null)
  const [result, setResult] = useState(null)
  const [selected, setSelected] = useState(null)
  const [explanation, setExplanation] = useState('')
  const [loading, setLoading] = useState(false)
  const [explaining, setExplaining] = useState(false)
  const [error, setError] = useState('')
  const [compareIds, setCompareIds] = useState([])
  const [compareData, setCompareData] = useState(null)
  const [comparing, setComparing] = useState(false)
  const [itinerary, setItinerary] = useState(null)
  const [itineraryLoading, setItineraryLoading] = useState(false)
  const [twin, setTwin] = useState(() => loadTwin())
  const [savedTrips, setSavedTrips] = useState(() => loadSavedTrips())
  const [extractedNote, setExtractedNote] = useState('')
  const debounceRef = useRef(null)
  const resultsRef = useRef(null)
  const itineraryRef = useRef(null)
  const prefsRef = useRef(prefs)
  prefsRef.current = prefs

  useEffect(() => {
    fetchMeta()
      .then(setMeta)
      .catch(() => setMeta(null))
  }, [])

  function payloadFrom(nextPrefs) {
    return {
      ...nextPrefs,
      experience_query: nextPrefs.experience_query || null,
    }
  }

  async function runRecommend(nextPrefs = prefsRef.current, { scroll = false, track = true } = {}) {
    setLoading(true)
    setError('')
    setCompareData(null)
    setItinerary(null)
    try {
      const data = await recommend(payloadFrom(nextPrefs))
      setResult(data)
      setSelected(data.matches[0] || null)
      setExplanation('')
      setStage('results')
      if (track) {
        setTwin(updateTwinFromSearch(nextPrefs, data.matches))
      }
      if (scroll) {
        requestAnimationFrame(() => {
          resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        })
      }
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  function handleSubmit() {
    runRecommend(prefs, { scroll: true })
  }

  function handleWhatIf(nextPrefs) {
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      runRecommend(nextPrefs, { track: false })
    }, 280)
  }

  async function handleExperienceSearch(query) {
    setLoading(true)
    setError('')
    setExtractedNote('')
    try {
      const data = await experienceSearch({
        query,
        starting_city: prefs.starting_city,
        passport: prefs.passport,
        budget_inr: prefs.budget_inr,
        days: prefs.days,
        max_flight_hours: prefs.max_flight_hours,
      })
      const nextPrefs = {
        ...prefs,
        ...data.preferences,
        experience_query: query,
      }
      setPrefs(nextPrefs)
      setResult(data.result)
      setSelected(data.result.matches[0] || null)
      setExplanation('')
      setItinerary(null)
      setExtractedNote(
        `Interpreted as: ${(data.preferences.travel_styles || []).join(', ') || 'open styles'}` +
          (data.preferences.avoid?.length ? ` · avoid ${data.preferences.avoid.join(', ')}` : ''),
      )
      setTwin(updateTwinFromSearch(nextPrefs, data.result.matches))
      setStage('results')
    } catch (err) {
      setError(err.message || 'Experience search failed')
    } finally {
      setLoading(false)
    }
  }

  async function handleExplain() {
    if (!selected) return
    setExplaining(true)
    try {
      const data = await explain(selected.id, payloadFrom(prefs))
      setExplanation(data.explanation)
    } catch (err) {
      setExplanation(err.message || 'Could not generate explanation')
    } finally {
      setExplaining(false)
    }
  }

  async function handleItinerary() {
    if (!selected) return
    setItineraryLoading(true)
    setError('')
    try {
      const plan = await fetchItinerary(selected.id, payloadFrom(prefs))
      setItinerary(plan)
      requestAnimationFrame(() => {
        itineraryRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      })
    } catch (err) {
      setError(err.message || 'Could not build itinerary')
    } finally {
      setItineraryLoading(false)
    }
  }

  function toggleCompare(match) {
    setCompareIds((ids) => {
      if (ids.includes(match.id)) return ids.filter((id) => id !== match.id)
      if (ids.length >= 3) return [...ids.slice(1), match.id]
      return [...ids, match.id]
    })
    setCompareData(null)
  }

  async function runCompare() {
    if (compareIds.length < 2) return
    setComparing(true)
    setError('')
    try {
      const data = await compareDestinations(compareIds, payloadFrom(prefs))
      setCompareData(data)
      setStage('results')
    } catch (err) {
      setError(err.message || 'Compare failed')
    } finally {
      setComparing(false)
    }
  }

  function handleSave() {
    if (!selected) return
    const next = saveTrip({
      destinationId: selected.id,
      destinationName: selected.name,
      destinationCountry: selected.country,
      matchPercent: selected.match_percent,
      budgetInr: prefs.budget_inr,
      days: prefs.days,
      prefs: { ...prefs },
      match: selected,
    })
    setSavedTrips(next)
    setTwin(updateTwinFromSearch(prefs, [selected]))
  }

  function handleOpenSaved(trip) {
    if (trip.prefs) setPrefs(trip.prefs)
    if (trip.match) {
      setSelected(trip.match)
      setResult({
        matches: [trip.match],
        trip_dna: trip.match.trip_dna || {},
        query_summary: `Saved trip · ${trip.destinationName}`,
      })
      setStage('results')
    } else if (trip.prefs) {
      runRecommend(trip.prefs, { scroll: true })
    }
  }

  const savedSelected = savedTrips.some((t) => t.destinationId === selected?.id)

  return (
    <div className="app">
      <div className="atmosphere" aria-hidden="true" />

      <header className="topbar">
        <button type="button" className="brand" onClick={() => setStage('hero')}>
          <span className="brand-mark">R</span>
          <span className="brand-text">
            Reverse
            <small>Travel Planner</small>
          </span>
        </button>
        <nav>
          <button type="button" onClick={() => setStage('hero')}>
            Home
          </button>
          <button type="button" onClick={() => setStage('form')}>
            Plan
          </button>
          {result && (
            <button type="button" onClick={() => setStage('results')}>
              Matches
            </button>
          )}
          <button type="button" onClick={() => setStage('twin')}>
            Twin
          </button>
          <button type="button" onClick={() => setStage('saved')}>
            Saved
          </button>
        </nav>
      </header>

      {stage === 'hero' && (
        <section className="hero-screen">
          <div className="hero-copy">
            <p className="brand-lockup">Reverse Travel Planner</p>
            <h1>Don&apos;t choose a destination. Choose the experience.</h1>
            <p className="hero-sub">
              Constraints and feelings in — ranked cities, explainable scores, itineraries, and a Travel Twin
              that learns you over time.
            </p>
            <div className="hero-cta">
              <button type="button" className="primary-btn" onClick={() => setStage('form')}>
                Tell us about your ideal trip
              </button>
              <button
                type="button"
                className="ghost-btn"
                onClick={() => runRecommend(DEFAULT_PREFS, { scroll: true })}
              >
                Try a demo search
              </button>
            </div>
          </div>
          <div className="hero-visual" aria-hidden="true">
            <div className="orbit orbit-a" />
            <div className="orbit orbit-b" />
            <div className="map-glow" />
            <ul className="floating-tags">
              <li>₹40k · 5 days</li>
              <li>No tourist traps</li>
              <li>Max 4h flight</li>
              <li>Café mornings</li>
            </ul>
          </div>
        </section>
      )}

      {stage === 'hero' && (
        <main className="page hero-below">
          <ExperienceSearch
            examples={meta?.experience_examples}
            prefs={prefs}
            onSearch={handleExperienceSearch}
            loading={loading}
          />
        </main>
      )}

      {stage === 'form' && (
        <main className="page">
          <TripForm
            prefs={prefs}
            setPrefs={setPrefs}
            meta={meta}
            onSubmit={handleSubmit}
            loading={loading}
          />
          <ExperienceSearch
            examples={meta?.experience_examples}
            prefs={prefs}
            onSearch={handleExperienceSearch}
            loading={loading}
          />
          {error && <p className="error">{error}</p>}
        </main>
      )}

      {stage === 'twin' && (
        <main className="page">
          <TravelTwin twin={twin} />
        </main>
      )}

      {stage === 'saved' && (
        <main className="page">
          <SavedTrips
            trips={savedTrips}
            onOpen={handleOpenSaved}
            onRemove={(id) => setSavedTrips(removeSavedTrip(id))}
          />
        </main>
      )}

      {stage === 'results' && result && (
        <main className="page results-page" ref={resultsRef}>
          <header className="results-header">
            <p className="eyebrow">AI computed</p>
            <h2>Your destination matches</h2>
            <p className="lede">{result.query_summary}</p>
            {extractedNote && <p className="extracted-note">{extractedNote}</p>}
            <div className="results-toolbar">
              <button type="button" className="ghost-btn" onClick={() => setStage('form')}>
                Edit preferences
              </button>
              <button
                type="button"
                className="ghost-btn"
                disabled={compareIds.length < 2 || comparing}
                onClick={runCompare}
              >
                {comparing ? 'Comparing…' : `Compare selected (${compareIds.length}/3)`}
              </button>
            </div>
          </header>

          <WhatIf prefs={prefs} setPrefs={setPrefs} onRecalculate={handleWhatIf} loading={loading} />
          <TripDna dna={result.trip_dna} />

          {compareData && <CompareView data={compareData} onClose={() => setCompareData(null)} />}

          <div className="results-layout">
            <div className="match-list">
              {result.matches.map((m, i) => (
                <MatchCard
                  key={m.id}
                  match={m}
                  rank={i + 1}
                  selected={selected?.id === m.id}
                  compareSelected={compareIds.includes(m.id)}
                  onToggleCompare={toggleCompare}
                  onSelect={(match) => {
                    setSelected(match)
                    setExplanation('')
                    setItinerary(null)
                  }}
                />
              ))}
              {!result.matches.length && (
                <p className="empty-matches">No destinations fit those constraints. Loosen budget or flight time.</p>
              )}
            </div>
            <MatchDetail
              match={selected}
              explanation={explanation}
              explaining={explaining}
              onExplain={handleExplain}
              onGenerateItinerary={handleItinerary}
              itineraryLoading={itineraryLoading}
              onSave={handleSave}
              saved={savedSelected}
              compareSelected={compareIds.includes(selected?.id)}
              onToggleCompare={() => selected && toggleCompare(selected)}
            />
          </div>

          <div ref={itineraryRef}>
            <ItineraryPanel
              plan={itinerary}
              loading={itineraryLoading}
              onGenerate={handleItinerary}
              onClose={() => setItinerary(null)}
            />
          </div>
          {error && <p className="error">{error}</p>}
        </main>
      )}

      <footer className="site-footer">
        <p>Destination is the output — reverse planning from constraints to cities.</p>
      </footer>
    </div>
  )
}
