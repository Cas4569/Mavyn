import { useEffect, useState } from 'react'
import { ArrowRight, CircleAlert, LoaderCircle, Star } from 'lucide-react'
import { api } from '../api.js'
import AppLink from '../components/AppLink.jsx'
import AnimatedContent from '../components/AnimatedContent.jsx'
import { ProductArtwork } from '../components/ProductCard.jsx'
import ResearchSources from '../components/ResearchSources.jsx'

const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
})

const formatPrice = (value) => (value == null ? 'Unavailable' : currency.format(value))
const formatRating = (value) => (value == null ? 'Unavailable' : `${value.toFixed(1)}/5`)
const formatCount = (value) => (value == null ? 'Unavailable' : value.toLocaleString('en-IN'))

const swotLabels = [
  ['Strengths', 'strengths'],
  ['Weaknesses', 'weaknesses'],
  ['Opportunities', 'opportunities'],
  ['Threats', 'threats'],
]

export default function ProductIntelligencePage({ productId, navigate }) {
  const [state, setState] = useState({ loading: true, data: null, error: '' })
  const [reviewState, setReviewState] = useState({ loading: false, data: null, error: '' })

  useEffect(() => {
    let active = true
    Promise.all([
      api.product(productId),
      api.productComparison(productId),
      api.productStrategy(productId),
    ])
      .then(([detail, comparison, strategy]) => {
        if (active) setState({ loading: false, data: { detail, comparison, strategy }, error: '' })
      })
      .catch((error) => {
        if (active) setState({ loading: false, data: null, error: error.message })
      })
    return () => {
      active = false
    }
  }, [productId])

  async function analyzeReviews() {
    setReviewState({ loading: true, data: null, error: '' })
    try {
      const data = await api.analyzeReviews(productId)
      setReviewState({ loading: false, data, error: '' })
    } catch (error) {
      setReviewState({ loading: false, data: null, error: error.message })
    }
  }

  if (state.loading) {
    return <div className="route-page empty-state" role="status"><LoaderCircle className="spin" size={20} /> Loading product intelligence</div>
  }
  if (state.error || !state.data) {
    return (
      <div className="route-page">
        <div className="notice notice-error" role="alert"><CircleAlert size={18} />{state.error || 'Product data is unavailable.'}</div>
        <AppLink className="text-link" to="/products" navigate={navigate}>Back to product catalog</AppLink>
      </div>
    )
  }

  const { detail, comparison, strategy } = state.data
  const product = detail.product

  return (
    <div className="route-page intelligence-page">
      <nav className="breadcrumbs" aria-label="Breadcrumb">
        <AppLink to="/products" navigate={navigate}>Product catalog</AppLink>
        <span aria-hidden="true">/</span>
        <span aria-current="page">{product.name}</span>
      </nav>

      <section className="product-intro">
        <div className="product-intro-art"><ProductArtwork product={product} /></div>
        <div className="product-intro-copy">
          <p className="eyebrow">{product.category_id} / PRODUCT INTELLIGENCE</p>
          <h1>{product.name}</h1>
          <p className="page-lead">{product.tagline || 'Live product research and market signals.'}</p>
          <span className="source-badge">LIVE / GOOGLE SEARCH</span>
          <div className="product-metrics">
            <span><strong>{formatPrice(product.price_inr)}</strong> verified listed price</span>
            <span><Star size={14} aria-hidden="true" /><strong>{formatRating(product.rating)}</strong> public rating</span>
            <span><strong>{formatCount(product.review_count)}</strong> listed reviews</span>
          </div>
          <AppLink
            className="primary-button"
            to={`/studio?product_id=${encodeURIComponent(product.id)}`}
            navigate={navigate}
          >
            Create campaign drafts <ArrowRight size={16} aria-hidden="true" />
          </AppLink>
        </div>
      </section>

      <section className="page-section" aria-labelledby="comparison-title">
        <div className="page-heading compact">
          <p className="eyebrow">CATEGORY BENCHMARK</p>
          <h2 id="comparison-title">Competitor comparison</h2>
          <p>Only values found in cited public sources are shown; unavailable fields are not estimated.</p>
        </div>
        <div className="data-table-wrap">
          <table className="data-table">
            <caption>Dot &amp; Key product and researched competitors</caption>
            <thead>
              <tr><th scope="col">Product</th><th scope="col">Brand</th><th scope="col">Price</th><th scope="col">Rating</th><th scope="col">Reviews</th></tr>
            </thead>
            <tbody>
              <tr className="data-table-featured">
                <th scope="row">{product.name}</th><td>Dot &amp; Key</td>
                <td>{formatPrice(product.price_inr)}</td><td>{formatRating(product.rating)}</td>
                <td>{formatCount(product.review_count)}</td>
              </tr>
              {detail.competitors.map((competitor) => (
                <tr key={competitor.id}>
                  <th scope="row">{competitor.name}</th><td>{competitor.brand}</td>
                  <td>{formatPrice(competitor.price_inr)}</td><td>{formatRating(competitor.rating)}</td>
                  <td>{formatCount(competitor.review_count)}</td>
                </tr>
              ))}
              {!detail.competitors.length && (
                <tr><td colSpan="5">No cited competitor records were found for this query.</td></tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="comparison-summary">
          <p>{comparison.price_analysis.details}</p>
          <p>{comparison.rating_analysis.details}</p>
        </div>
        <ResearchSources sources={detail.sources} fetchedAt={detail.fetched_at} />
      </section>

      <section className="page-section" aria-labelledby="market-brief-title">
        <div className="page-heading compact">
          <p className="eyebrow">PRODUCT-SPECIFIC SIGNALS</p>
          <h2 id="market-brief-title">Market brief</h2>
          <p>Recommendations are based on the cited product, competitor, and public review records above.</p>
        </div>
        <div className="swot-grid">
          {swotLabels.map(([label, key]) => (
            <article className="brief-panel" key={key}>
              <h3>{label}</h3>
              {strategy.swot[key].length ? (
                <ul className="insight-list">
                  {strategy.swot[key].map((item) => <li key={item}>{item}</li>)}
                </ul>
              ) : <p className="muted-copy">No repeated signal was detected in the retrieved records.</p>}
            </article>
          ))}
        </div>
        <div className="intelligence-columns">
          <article className="brief-panel">
            <h3>Market gaps to validate</h3>
            {strategy.market_gaps.length ? strategy.market_gaps.map((gap) => (
              <div className="evidence-item" key={gap.description}>
                <span className={`severity severity-${gap.severity}`}>{gap.severity} signal</span>
                <p>{gap.description}</p>
                <small>{gap.evidence}</small>
              </div>
            )) : <p className="muted-copy">No repeated complaint emerged from the retrieved review excerpts.</p>}
          </article>
          <article className="brief-panel">
            <h3>Recommended tests</h3>
            {strategy.opportunities.length ? (
              <ul className="opportunity-list">
                {strategy.opportunities.map((item) => (
                  <li key={item.title}><strong>{item.title}</strong><span>{item.description}</span></li>
                ))}
              </ul>
            ) : <p className="muted-copy">More evidence is needed to recommend a product or campaign test.</p>}
          </article>
        </div>
        <p className="forecast-note">{strategy.forecast_note}</p>
      </section>

      <section className="page-section review-section" aria-labelledby="review-title">
        <div className="page-heading compact">
          <p className="eyebrow">VOICE OF CUSTOMER</p>
          <h2 id="review-title">Review analysis</h2>
          <p>Analyze public review excerpts found through Google Search. Excerpts may not represent all customers.</p>
        </div>
        <button className="primary-button" type="button" onClick={analyzeReviews} disabled={reviewState.loading}>
          {reviewState.loading ? <><LoaderCircle className="spin" size={16} /> Analyzing reviews</> : 'Analyze public review excerpts'}
        </button>
        {reviewState.error && <p className="inline-error" role="alert">{reviewState.error}</p>}
        {reviewState.data && (
          <AnimatedContent className="review-analysis-result">
            <div className="sentiment-heading">
              <strong>{reviewState.data.sentiment.positive_pct}% positive</strong>
              <span>{reviewState.data.sentiment.total} retrieved excerpts</span>
            </div>
            <div className="sentiment-bar" aria-label={`${reviewState.data.sentiment.positive_pct}% positive sentiment`}>
              <span style={{ width: `${reviewState.data.sentiment.positive_pct}%` }} />
            </div>
            <div className="sentiment-stats">
              <span>{reviewState.data.sentiment.positive} positive</span>
              <span>{reviewState.data.sentiment.neutral} neutral</span>
              <span>{reviewState.data.sentiment.negative} negative</span>
            </div>
            <ul className="insight-list">
              {reviewState.data.key_insights.map((insight) => <li key={insight}>{insight}</li>)}
            </ul>
          </AnimatedContent>
        )}
        <details className="research-reviews">
          <summary>View retrieved public review excerpts ({detail.reviews.length})</summary>
          {detail.reviews.length ? (
            <ul>
              {detail.reviews.map((review) => (
                <li key={`${review.source.url}-${review.text}`}>
                  <p>{review.text}</p>
                  <a href={review.source.url} target="_blank" rel="noreferrer">
                    {review.source.title}
                  </a>
                </li>
              ))}
            </ul>
          ) : <p className="muted-copy">No public review excerpts were found in this search.</p>}
        </details>
      </section>
    </div>
  )
}
