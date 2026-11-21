import { useEffect, useState } from 'react'
import { CircleAlert, LoaderCircle, Sparkles } from 'lucide-react'
import { api } from '../api.js'
import AnimatedContent from '../components/AnimatedContent.jsx'
import ResearchSources from '../components/ResearchSources.jsx'

export default function CreativeStudioPage() {
  const [products, setProducts] = useState([])
  const [selectedProductId, setSelectedProductId] = useState(
    () => new URLSearchParams(window.location.search).get('product_id') || '',
  )
  const [loadingProducts, setLoadingProducts] = useState(true)
  const [error, setError] = useState('')
  const [content, setContent] = useState(null)
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    let active = true
    api.dotAndKeyProducts()
      .then((result) => {
        if (!Array.isArray(result.products)) {
          throw new Error('The backend returned an invalid product list.')
        }
        if (!active) return
        setProducts(result.products)
        setSelectedProductId((current) => (
          result.products.some((product) => product.id === current)
            ? current
            : result.products[0]?.id || ''
        ))
      })
      .catch((requestError) => {
        if (active) setError(requestError.message)
      })
      .finally(() => {
        if (active) setLoadingProducts(false)
      })

    return () => {
      active = false
    }
  }, [])

  async function generateContent() {
    if (!selectedProductId) return
    setGenerating(true)
    setContent(null)
    setError('')
    try {
      setContent(await api.generateContent(selectedProductId))
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="route-page studio-page">
      <header className="page-heading">
        <p className="eyebrow">MAVYN / CREATIVE STUDIO</p>
        <h1>Turn a product brief into drafts.</h1>
        <p className="page-lead">
          Gemini turns live product, competitor, and public review evidence into e-commerce copy,
          platform ads, video scripts, and storyboards.
        </p>
      </header>

      <section className="studio-controls" aria-labelledby="studio-product-label">
        <label id="studio-product-label" htmlFor="studio-product">Product</label>
        <select
          id="studio-product"
          value={selectedProductId}
          onChange={(event) => {
            setSelectedProductId(event.target.value)
            setContent(null)
          }}
          disabled={loadingProducts || !products.length}
        >
          {products.map((product) => <option key={product.id} value={product.id}>{product.name}</option>)}
        </select>
        <button className="primary-button" type="button" onClick={generateContent} disabled={generating || !selectedProductId}>
          {generating
            ? <><LoaderCircle className="spin" size={16} aria-hidden="true" /> Generating with Gemini</>
            : <><Sparkles size={16} aria-hidden="true" /> Generate with Gemini</>}
        </button>
        <span className="source-badge">GEMINI / LIVE SEARCH EVIDENCE</span>
      </section>

      {loadingProducts && <p className="loading-line" role="status"><LoaderCircle className="spin" size={17} /> Loading products</p>}
      {error && <div className="notice notice-error" role="alert"><CircleAlert size={18} />{error}</div>}
      {!content && !generating && !error && !loadingProducts && (
        <p className="studio-empty">Choose a product and generate a draft pack to review here.</p>
      )}

      {content && (
        <AnimatedContent className="studio-results">
          <div className="studio-results-heading">
            <div>
              <p className="eyebrow">DRAFT OUTPUT</p>
              <h2>{products.find((product) => product.id === content.product_id)?.name}</h2>
            </div>
            <span className="source-badge">
              {`GEMINI GENERATED${content.model ? ` · ${content.model}` : ''}`}
            </span>
          </div>

          <section className="studio-output-section" aria-labelledby="ad-copy-title">
            <h3 id="ad-copy-title">Platform ad copy</h3>
            <div className="studio-output-grid">
              {content.ad_copy.map((copy) => (
                <article className="studio-output-card" key={copy.platform}>
                  <p className="card-kicker">{copy.platform}</p>
                  <h4>{copy.headline}</h4>
                  <p>{copy.primary_text}</p>
                  <div className="output-meta">
                    <span>CTA: {copy.cta}</span>
                    <span>{copy.character_count} characters</span>
                    {copy.hashtags.length > 0 && <span>Hashtags: {copy.hashtags.map((tag) => `#${tag}`).join(' ')}</span>}
                  </div>
                </article>
              ))}
            </div>
          </section>

          {content.product_description && (
            <section className="studio-output-section" aria-labelledby="description-title">
              <h3 id="description-title">Product page description</h3>
              <article className="studio-output-card">
                <p>{content.product_description.short_description}</p>
                <p className="generated-description">{content.product_description.long_description}</p>
                {content.product_description.key_benefits.length > 0 && (
                  <ul className="insight-list">
                    {content.product_description.key_benefits.map((benefit) => <li key={benefit}>{benefit}</li>)}
                  </ul>
                )}
                {content.product_description.ingredients_highlight.length > 0 && (
                  <p className="output-meta">
                    Ingredients to verify: {content.product_description.ingredients_highlight.join(' · ')}
                  </p>
                )}
                {content.product_description.usage_instructions && (
                  <p className="output-meta">{content.product_description.usage_instructions}</p>
                )}
              </article>
            </section>
          )}

          {content.listing_content && (
            <section className="studio-output-section" aria-labelledby="listing-title">
              <h3 id="listing-title">Marketplace listing</h3>
              <article className="studio-output-card">
                <h4>{content.listing_content.title}</h4>
                <ul className="insight-list">
                  {content.listing_content.bullet_points.map((point) => <li key={point}>{point}</li>)}
                </ul>
                <p className="output-meta">Search terms: {content.listing_content.search_terms.join(' · ')}</p>
                {content.listing_content.enhanced_content && (
                  <p className="generated-description">{content.listing_content.enhanced_content}</p>
                )}
              </article>
            </section>
          )}

          <section className="studio-output-section" aria-labelledby="video-title">
            <h3 id="video-title">Video concepts</h3>
            <div className="studio-output-grid">
              {content.ad_scripts.map((script) => (
                <article className="studio-output-card" key={`${script.format}-${script.duration_seconds}`}>
                  <p className="card-kicker">{script.format} / {script.duration_seconds}s</p>
                  <h4>{script.hook}</h4>
                  <p className="generated-description">{script.script}</p>
                  <span className="output-meta">CTA: {script.cta}</span>
                </article>
              ))}
              {content.video_concepts.map((concept) => (
                <article className="studio-output-card" key={concept.concept_name}>
                  <p className="card-kicker">VIDEO CONCEPT</p>
                  <h4>{concept.concept_name}</h4>
                  <p>{concept.logline}</p>
                  <p className="generated-description">{concept.key_message}</p>
                  <p className="output-meta">Audience hypothesis: {concept.target_audience}</p>
                  {concept.scripts.map((script) => (
                    <div key={`${concept.concept_name}-${script.format}`}>
                      <p className="card-kicker">{script.format} / {script.duration_seconds}s</p>
                      <h4>{script.hook}</h4>
                      <p className="generated-description">{script.script}</p>
                      <span className="output-meta">CTA: {script.cta}</span>
                    </div>
                  ))}
                  <details className="storyboard-details">
                    <summary>View concept storyboard ({concept.storyboard.frames.length} frames)</summary>
                    <ol>
                      {concept.storyboard.frames.map((frame) => (
                        <li key={`${concept.concept_name}-${frame.frame_number}`}>
                          <strong>{frame.duration_seconds}s</strong> {frame.visual_description}
                          {frame.audio_cue && <span>{frame.audio_cue}</span>}
                        </li>
                      ))}
                    </ol>
                  </details>
                  {concept.production_notes.map((note) => <small className="production-note" key={note}>{note}</small>)}
                </article>
              ))}
            </div>
            {content.storyboard && (
              <details className="storyboard-details">
                <summary>View {content.storyboard.frames.length}-frame storyboard</summary>
                <ol>
                  {content.storyboard.frames.map((frame) => (
                    <li key={frame.frame_number}>
                      <strong>{frame.duration_seconds}s</strong> {frame.visual_description}
                      {frame.audio_cue && <span>{frame.audio_cue}</span>}
                    </li>
                  ))}
                </ol>
              </details>
            )}
          </section>
          <ResearchSources
            sources={content.research_sources}
            fetchedAt={content.research_fetched_at}
          />
          <p className="forecast-note">
            Gemini used live Google Search-grounded product, competitor, and public review records.
            Verify every product claim and specification before publication.
          </p>
        </AnimatedContent>
      )}
    </div>
  )
}
