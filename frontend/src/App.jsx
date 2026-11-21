import { useEffect, useMemo, useState } from 'react'
import {
  ArrowUpRight,
  CircleAlert,
  Droplets,
  FlaskConical,
  Leaf,
  LoaderCircle,
  MessageSquareText,
  Package,
  Search,
  Sparkles,
  Star,
  Sun,
  Waves,
} from 'lucide-react'
import { api } from './api'
import './App.css'

const categoryIcons = {
  sunscreens: Sun,
  serums: FlaskConical,
  moisturizers: Droplets,
  cleansers: Waves,
  toners: Leaf,
}

const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
})

function ProductArtwork({ product }) {
  const [imageFailed, setImageFailed] = useState(false)

  if (!product.hero_image || imageFailed) {
    return (
      <div className="product-artwork product-artwork-fallback" aria-hidden="true">
        <Package size={34} strokeWidth={1.4} />
      </div>
    )
  }

  return (
    <img
      className="product-artwork"
      src={product.hero_image}
      alt={product.name}
      loading="lazy"
      onError={() => setImageFailed(true)}
    />
  )
}

function App() {
  const [health, setHealth] = useState(null)
  const [healthError, setHealthError] = useState('')
  const [categoryState, setCategoryState] = useState({
    loading: true,
    categories: [],
    error: '',
  })
  const [selectedCategoryId, setSelectedCategoryId] = useState('')
  const [selectedProductId, setSelectedProductId] = useState('')
  const [productState, setProductState] = useState({
    categoryId: '',
    products: [],
    error: '',
  })
  const [detailState, setDetailState] = useState({ productId: '', data: null, error: '' })
  const [search, setSearch] = useState('')
  const [reviewResult, setReviewResult] = useState(null)
  const [reviewLoadingFor, setReviewLoadingFor] = useState('')
  const [contentResult, setContentResult] = useState(null)
  const [contentLoadingFor, setContentLoadingFor] = useState('')

  useEffect(() => {
    let active = true

    api.health()
      .then((result) => {
        if (active) setHealth(result)
      })
      .catch((error) => {
        if (active) setHealthError(error.message)
      })

    api.categories()
      .then((result) => {
        if (!Array.isArray(result.categories)) {
          throw new Error('The backend returned an invalid categories response.')
        }
        if (!active) return
        setCategoryState({ loading: false, categories: result.categories, error: '' })
        setSelectedCategoryId((current) => current || result.categories[0]?.id || '')
      })
      .catch((error) => {
        if (active) {
          setCategoryState({ loading: false, categories: [], error: error.message })
        }
      })

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!selectedCategoryId) return undefined

    let active = true
    api.products(selectedCategoryId)
      .then((result) => {
        if (!Array.isArray(result.products)) {
          throw new Error('The backend returned an invalid products response.')
        }
        if (active) {
          setProductState({
            categoryId: selectedCategoryId,
            products: result.products,
            error: '',
          })
        }
      })
      .catch((error) => {
        if (active) {
          setProductState({ categoryId: selectedCategoryId, products: [], error: error.message })
        }
      })

    return () => {
      active = false
    }
  }, [selectedCategoryId])

  const products = useMemo(
    () => productState.categoryId === selectedCategoryId ? productState.products : [],
    [productState.categoryId, productState.products, selectedCategoryId],
  )
  const productsError = productState.categoryId === selectedCategoryId ? productState.error : ''
  const productsLoading = Boolean(selectedCategoryId) && productState.categoryId !== selectedCategoryId
  const selectedProduct =
    products.find((product) => product.id === selectedProductId) || products[0] || null
  const selectedCategory = categoryState.categories.find(
    (category) => category.id === selectedCategoryId,
  )
  const visibleProducts = useMemo(() => {
    const query = search.trim().toLowerCase()
    if (!query) return products
    return products.filter((product) => product.name.toLowerCase().includes(query))
  }, [products, search])

  const selectedProductIdForRequest = selectedProduct?.id

  useEffect(() => {
    if (!selectedProductIdForRequest) return undefined
    let active = true
    api.product(selectedProductIdForRequest)
      .then((result) => {
        if (active) setDetailState({ productId: selectedProductIdForRequest, data: result, error: '' })
      })
      .catch((error) => {
        if (active) {
          setDetailState({ productId: selectedProductIdForRequest, data: null, error: error.message })
        }
      })

    return () => {
      active = false
    }
  }, [selectedProductIdForRequest])

  const productDetail =
    detailState.productId === selectedProduct?.id ? detailState.data : null
  const detailError = detailState.productId === selectedProduct?.id ? detailState.error : ''
  const review = selectedProduct && reviewResult?.productId === selectedProduct.id
    ? reviewResult.data
    : null
  const reviewError = selectedProduct && reviewResult?.productId === selectedProduct.id
    ? reviewResult.error
    : ''
  const content = selectedProduct && contentResult?.productId === selectedProduct.id
    ? contentResult.data
    : null
  const contentError = selectedProduct && contentResult?.productId === selectedProduct.id
    ? contentResult.error
    : ''

  async function handleReviewAnalysis() {
    if (!selectedProduct) return
    const productId = selectedProduct.id
    setReviewLoadingFor(productId)
    setReviewResult({ productId, data: null, error: '' })
    try {
      const data = await api.analyzeReviews(productId)
      setReviewResult({ productId, data, error: '' })
    } catch (error) {
      setReviewResult({ productId, data: null, error: error.message })
    } finally {
      setReviewLoadingFor((current) => (current === productId ? '' : current))
    }
  }

  async function handleContentGeneration() {
    if (!selectedProduct) return
    const productId = selectedProduct.id
    setContentLoadingFor(productId)
    setContentResult({ productId, data: null, error: '' })
    try {
      const data = await api.generateContent(productId)
      setContentResult({ productId, data, error: '' })
    } catch (error) {
      setContentResult({ productId, data: null, error: error.message })
    } finally {
      setContentLoadingFor((current) => (current === productId ? '' : current))
    }
  }

  function chooseCategory(categoryId) {
    setSelectedCategoryId(categoryId)
    setSelectedProductId('')
    setSearch('')
  }

  const totalReviews = products.reduce((sum, product) => sum + product.review_count, 0)
  const apiOnline = health?.status === 'healthy'

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="MAVYN home">
          <span className="brand-mark"><Sparkles size={19} /></span>
          <span>MAVYN<span className="brand-period">.</span></span>
        </a>
        <div className="topbar-center">MARKET INTELLIGENCE <span> / </span> SKINCARE</div>
        <div className={`api-status ${apiOnline ? 'is-online' : healthError ? 'is-offline' : ''}`}>
          <span className="status-dot" />
          {apiOnline ? 'API connected' : healthError ? 'API unavailable' : 'Connecting'}
        </div>
      </header>

      <main className="main-content">
        <section className="welcome-panel">
          <div className="welcome-copy">
            <p className="eyebrow"><Sparkles size={14} /> YOUR SKINCARE INTELLIGENCE DESK</p>
            <h1>Make every insight<br />count<span>.</span></h1>
            <p className="welcome-description">
              Explore the Dot &amp; Key portfolio, understand customer feedback, and create
              campaign-ready content — all in one workspace.
            </p>
            <a className="text-link" href="http://localhost:8000/docs" target="_blank" rel="noreferrer">
              Explore the API <ArrowUpRight size={16} />
            </a>
          </div>
          <div className="welcome-art" aria-hidden="true">
            <div className="art-orbit orbit-one" />
            <div className="art-orbit orbit-two" />
            <div className="art-orbit orbit-three" />
            <div className="art-center"><Sparkles size={34} strokeWidth={1.3} /></div>
            <span className="art-label art-label-top">INSIGHT</span>
            <span className="art-label art-label-bottom">IMPACT</span>
          </div>
        </section>

        {healthError && (
          <div className="notice notice-error" role="alert">
            <CircleAlert size={18} />
            <span>Couldn’t reach the backend: {healthError}. Start it with the steps in the README.</span>
          </div>
        )}

        <section className="stats-row" aria-label="Portfolio summary">
          <div className="stat-card">
            <span className="stat-icon"><Package size={18} /></span>
            <div><strong>{categoryState.loading ? '—' : categoryState.categories.length}</strong><span>Categories</span></div>
          </div>
          <div className="stat-card">
            <span className="stat-icon"><Sparkles size={18} /></span>
            <div><strong>{productsLoading ? '—' : products.length}</strong><span>Products in view</span></div>
          </div>
          <div className="stat-card">
            <span className="stat-icon"><MessageSquareText size={18} /></span>
            <div><strong>{productsLoading ? '—' : totalReviews.toLocaleString('en-IN')}</strong><span>Customer reviews</span></div>
          </div>
          <div className="sample-note"><span className="sample-dot" /> Demo data from your local API</div>
        </section>

        <section className="catalog-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">THE PORTFOLIO</p>
              <h2>Explore products</h2>
            </div>
            <p className="section-subtitle">Choose a category to see products and insights.</p>
          </div>

          <div className="catalog-layout">
            <aside className="category-panel">
              <p className="panel-label">CATEGORIES</p>
              {categoryState.loading && <div className="loading-line"><LoaderCircle className="spin" size={17} /> Loading categories</div>}
              {categoryState.error && <p className="inline-error">{categoryState.error}</p>}
              <div className="category-list">
                {categoryState.categories.map((category) => {
                  const CategoryIcon = categoryIcons[category.id] || Sparkles
                  return (
                    <button
                      className={`category-button ${category.id === selectedCategoryId ? 'active' : ''}`}
                      key={category.id}
                      type="button"
                      onClick={() => chooseCategory(category.id)}
                    >
                      <span className="category-icon"><CategoryIcon size={17} /></span>
                      <span className="category-name">{category.name}</span>
                      <span className="category-count">{category.product_count}</span>
                    </button>
                  )
                })}
              </div>
              <div className="category-hint">
                <Sparkles size={16} />
                <p>Product, review and content data are served by your local backend.</p>
              </div>
            </aside>

            <div className="catalog-main">
              <div className="catalog-toolbar">
                <div>
                  <h3>{selectedCategory?.name || 'Products'}</h3>
                  <span>{products.length} Dot &amp; Key {products.length === 1 ? 'product' : 'products'}</span>
                </div>
                <label className="search-box">
                  <Search size={16} />
                  <input
                    aria-label="Search products"
                    placeholder="Search products"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                  />
                </label>
              </div>

              {productsLoading && <div className="empty-state"><LoaderCircle className="spin" size={22} /> Loading products…</div>}
              {productsError && <div className="notice notice-error" role="alert"><CircleAlert size={18} />{productsError}</div>}
              {!productsLoading && !productsError && visibleProducts.length === 0 && (
                <div className="empty-state">
                  {products.length ? 'No products match your search.' : 'No products are available in this category.'}
                </div>
              )}
              {!productsLoading && !productsError && visibleProducts.length > 0 && (
                <div className="product-grid">
                  {visibleProducts.map((product) => (
                    <button
                      className={`product-card ${product.id === selectedProduct?.id ? 'selected' : ''}`}
                      key={product.id}
                      type="button"
                      onClick={() => setSelectedProductId(product.id)}
                    >
                      <div className="product-image-wrap">
                        <ProductArtwork product={product} />
                        <span className="product-source">DOT &amp; KEY</span>
                      </div>
                      <div className="product-card-body">
                        <span className="product-category">{selectedCategory?.name}</span>
                        <h4>{product.name}</h4>
                        <p className="product-tagline">{product.tagline || 'Everyday skincare, made simple.'}</p>
                        <div className="product-card-meta">
                          <strong>{currency.format(product.price_inr)}</strong>
                          <span><Star size={14} fill="currentColor" /> {product.rating.toFixed(1)} <i>({product.review_count.toLocaleString('en-IN')})</i></span>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>

        {selectedProduct && (
          <section className="workspace-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">PRODUCT WORKSPACE</p>
                <h2>Turn data into direction</h2>
              </div>
              <span className="selected-product-label">{selectedProduct.name}</span>
            </div>

            <div className="workspace-grid">
              <article className="workspace-card product-detail-card">
                <div className="workspace-card-heading">
                  <div><span className="card-kicker">PRODUCT SNAPSHOT</span><h3>At a glance</h3></div>
                  <span className="source-badge">SAMPLE DATA</span>
                </div>
                <div className="selected-product-summary">
                  <ProductArtwork product={selectedProduct} />
                  <div>
                    <h4>{selectedProduct.name}</h4>
                    <p>{selectedProduct.tagline || 'Explore customer response and competitive context for this product.'}</p>
                    <div className="summary-meta">
                      <strong>{currency.format(selectedProduct.price_inr)}</strong>
                      <span><Star size={14} fill="currentColor" /> {selectedProduct.rating.toFixed(1)}</span>
                      <span>{selectedProduct.review_count.toLocaleString('en-IN')} reviews</span>
                    </div>
                  </div>
                </div>
                <div className="competitor-heading">
                  <span className="card-kicker">COMPETITIVE SET</span>
                  <span>{productDetail?.competitors?.length ?? '—'} products</span>
                </div>
                {detailError && <p className="inline-error">{detailError}</p>}
                {!productDetail && !detailError && <div className="loading-line"><LoaderCircle className="spin" size={16} /> Loading product details</div>}
                {productDetail?.competitors?.length > 0 && (
                  <div className="competitor-list">
                    {productDetail.competitors.slice(0, 3).map((competitor) => (
                      <div className="competitor-row" key={competitor.id}>
                        <span className="competitor-avatar">{competitor.brand?.slice(0, 1) || 'C'}</span>
                        <span className="competitor-name"><strong>{competitor.name}</strong><small>{competitor.brand}</small></span>
                        <span className="competitor-price">{currency.format(competitor.price_inr)}</span>
                        <span className="competitor-rating"><Star size={12} fill="currentColor" /> {competitor.rating.toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                )}
              </article>

              <article className="workspace-card insight-card">
                <div className="workspace-card-heading">
                  <div><span className="card-kicker">VOICE OF CUSTOMER</span><h3>Review pulse</h3></div>
                  <span className="insight-icon"><MessageSquareText size={18} /></span>
                </div>
                <p className="card-description">Analyze the sample customer reviews for recurring praise and complaints.</p>
                <button
                  className="primary-button"
                  type="button"
                  onClick={handleReviewAnalysis}
                  disabled={reviewLoadingFor === selectedProduct.id}
                >
                  {reviewLoadingFor === selectedProduct.id
                    ? <><LoaderCircle className="spin" size={16} /> Analyzing reviews…</>
                    : <>Analyze sample reviews <ArrowUpRight size={16} /></>}
                </button>
                {reviewError && <p className="inline-error" role="alert">{reviewError}</p>}
                {review && (
                  <div className="result-block">
                    <div className="sentiment-heading">
                      <strong>{review.sentiment.positive_pct}% positive</strong>
                      <span>{review.sentiment.total} reviews · {review.source} analysis</span>
                    </div>
                    <div className="sentiment-bar" aria-label={`${review.sentiment.positive_pct}% positive sentiment`}>
                      <span style={{ width: `${review.sentiment.positive_pct}%` }} />
                    </div>
                    <div className="sentiment-stats">
                      <span><i className="dot-positive" /> {review.sentiment.positive} positive</span>
                      <span><i className="dot-neutral" /> {review.sentiment.neutral} neutral</span>
                      <span><i className="dot-negative" /> {review.sentiment.negative} negative</span>
                    </div>
                    {review.key_insights?.length > 0 && (
                      <ul className="insight-list">
                        {review.key_insights.slice(0, 3).map((insight) => <li key={insight}>{insight}</li>)}
                      </ul>
                    )}
                  </div>
                )}
              </article>

              <article className="workspace-card content-card">
                <div className="workspace-card-heading">
                  <div><span className="card-kicker">CREATIVE STUDIO</span><h3>Campaign starter</h3></div>
                  <span className="insight-icon"><Sparkles size={18} /></span>
                </div>
                <p className="card-description">Generate sample ad copy and product descriptions using the backend content endpoint.</p>
                <button
                  className="secondary-button"
                  type="button"
                  onClick={handleContentGeneration}
                  disabled={contentLoadingFor === selectedProduct.id}
                >
                  {contentLoadingFor === selectedProduct.id
                    ? <><LoaderCircle className="spin" size={16} /> Creating content…</>
                    : <>Generate campaign content <ArrowUpRight size={16} /></>}
                </button>
                {contentError && <p className="inline-error" role="alert">{contentError}</p>}
                {content && (
                  <div className="result-block content-result">
                    <span className="result-label">{content.ad_copy?.[0]?.platform || 'PRODUCT'} · {content.source} content</span>
                    {content.ad_copy?.[0] && (
                      <div className="generated-copy">
                        <strong>{content.ad_copy[0].headline}</strong>
                        <p>{content.ad_copy[0].primary_text}</p>
                      </div>
                    )}
                    {content.product_description?.short_description && (
                      <p className="generated-description">{content.product_description.short_description}</p>
                    )}
                  </div>
                )}
              </article>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <span>© MAVYN · Skincare market intelligence</span>
        <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">Backend API docs <ArrowUpRight size={14} /></a>
      </footer>
    </div>
  )
}

export default App
