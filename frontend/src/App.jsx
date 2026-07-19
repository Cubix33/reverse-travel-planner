import { useEffect, useRef, useState } from 'react'
import { explain, fetchMeta, recommend } from './api'
import { DEFAULT_PREFS } from './defaults'
import MatchCard from './components/MatchCard'
import MatchDetail from './components/MatchDetail'
import TripDna from './components/TripDna'
import TripForm from './components/TripForm'
import WhatIf from './components/WhatIf'
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
  const debounceRef = useRef(null)
  const resultsRef = useRef(null)
  const prefsRef = useRef(prefs)
  prefsRef.current = prefs

  useEffect(() => {
    fetchMeta()
      .then(setMeta)
      .catch(() => setMeta(null))
  }, [])

  async function runRecommend(nextPrefs = prefsRef.current, { scroll = false } = {}) {
    setLoading(true)
    setError('')
    try {
      const payload = {
        ...nextPrefs,
        experience_query: nextPrefs.experience_query || null,
      }
      const data = await recommend(payload)
      setResult(data)
      setSelected(data.matches[0] || null)
      setExplanation('')
      setStage('results')
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
      runRecommend(nextPrefs)
    }, 280)
  }

  async function handleExplain() {
    if (!selected) return
    setExplaining(true)
    try {
      const data = await explain(selected.id, {
        ...prefs,
        experience_query: prefs.experience_query || null,
      })
      setExplanation(data.explanation)
    } catch (err) {
      setExplanation(err.message || 'Could not generate explanation')
    } finally {
      setExplaining(false)
    }
  }

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
          <button type="button" onClick={() => setStage('form')}>
            Plan
          </button>
          {result && (
            <button type="button" onClick={() => setStage('results')}>
              Matches
            </button>
          )}
        </nav>
      </header>

      {stage === 'hero' && (
        <section className="hero-screen">
          <div className="hero-copy">
            <p className="brand-lockup">Reverse Travel Planner</p>
            <h1>Don&apos;t choose a destination. Choose the experience.</h1>
            <p className="hero-sub">
              Budget, days, visa friction, weather, and vibe in — ranked cities out, with a clear why for every
              match.
            </p>
            <div className="hero-cta">
              <button type="button" className="primary-btn" onClick={() => setStage('form')}>
                Tell us about your ideal trip
              </button>
              <button
                type="button"
                className="ghost-btn"
                onClick={() => {
                  setStage('form')
                  setTimeout(() => runRecommend(DEFAULT_PREFS, { scroll: true }), 50)
                }}
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

      {stage === 'form' && (
        <main className="page">
          <TripForm
            prefs={prefs}
            setPrefs={setPrefs}
            meta={meta}
            onSubmit={handleSubmit}
            loading={loading}
          />
          {error && <p className="error">{error}</p>}
        </main>
      )}

      {stage === 'results' && result && (
        <main className="page results-page" ref={resultsRef}>
          <header className="results-header">
            <p className="eyebrow">AI computed</p>
            <h2>Your destination matches</h2>
            <p className="lede">{result.query_summary}</p>
            <button type="button" className="ghost-btn" onClick={() => setStage('form')}>
              Edit preferences
            </button>
          </header>

          <WhatIf prefs={prefs} setPrefs={setPrefs} onRecalculate={handleWhatIf} loading={loading} />
          <TripDna dna={result.trip_dna} />

          <div className="results-layout">
            <div className="match-list">
              {result.matches.map((m, i) => (
                <MatchCard
                  key={m.id}
                  match={m}
                  rank={i + 1}
                  selected={selected?.id === m.id}
                  onSelect={(match) => {
                    setSelected(match)
                    setExplanation('')
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
            />
          </div>
          {error && <p className="error">{error}</p>}
        </main>
      )}

      <footer className="site-footer">
        <p>Destination is the output — built for OpenAI Build Week.</p>
      </footer>
    </div>
  )
}
