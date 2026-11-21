import { lazy, Suspense, useCallback, useEffect, useState } from 'react'
import { ArrowUpRight } from 'lucide-react'
import { api } from './api.js'
import AppLink from './components/AppLink.jsx'
import HomePage from './pages/HomePage.jsx'
import './App.css'

const ProductCatalogPage = lazy(() => import('./pages/ProductCatalogPage.jsx'))
const ProductIntelligencePage = lazy(() => import('./pages/ProductIntelligencePage.jsx'))
const CreativeStudioPage = lazy(() => import('./pages/CreativeStudioPage.jsx'))
const MethodologyPage = lazy(() => import('./pages/MethodologyPage.jsx'))

function resolveRoute(location) {
  const url = new URL(location, window.location.origin)
  const productMatch = url.pathname.match(/^\/products\/([^/]+)$/)

  if (url.pathname === '/') return { name: 'home', path: url.pathname }
  if (url.pathname === '/products') return { name: 'catalog', path: url.pathname }
  if (productMatch) return { name: 'product', path: url.pathname, productId: productMatch[1] }
  if (url.pathname === '/studio') return { name: 'studio', path: url.pathname }
  if (url.pathname === '/methodology') return { name: 'methodology', path: url.pathname }
  return { name: 'not-found', path: url.pathname }
}

function NotFoundPage({ navigate }) {
  return (
    <section className="route-page not-found-page">
      <p className="eyebrow">PAGE NOT FOUND</p>
      <h1>This page is not in the MAVYN workspace.</h1>
      <AppLink className="primary-button" to="/products" navigate={navigate}>
        Open the product catalog
      </AppLink>
    </section>
  )
}

export default function App() {
  const [location, setLocation] = useState(
    () => `${window.location.pathname}${window.location.search}`,
  )
  const [apiState, setApiState] = useState({ status: 'connecting', error: '' })
  const route = resolveRoute(location)

  useEffect(() => {
    let active = true
    api.health()
      .then(() => {
        if (active) setApiState({ status: 'online', error: '' })
      })
      .catch((error) => {
        if (active) setApiState({ status: 'offline', error: error.message })
      })
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    const metadata = {
      home: {
        title: 'MAVYN | Dot & Key Market Intelligence',
        description: 'Explore Dot & Key skincare products, Google Search-grounded competitor comparisons, customer-review insights, and campaign drafts with MAVYN.',
      },
      catalog: {
        title: 'Product Catalog | MAVYN',
        description: 'Browse live Dot & Key catalog research and open product intelligence reports with cited competitor and review insights.',
      },
      product: {
        title: 'Product Intelligence | MAVYN',
        description: 'Compare cited competitors, review public customer feedback signals, and explore evidence-based product opportunities.',
      },
      studio: {
        title: 'Creative Studio | MAVYN',
        description: 'Generate product descriptions, marketplace listings, platform ads, video scripts, and storyboards from market evidence.',
      },
      methodology: {
        title: 'Data & Method | MAVYN',
        description: 'Learn how MAVYN uses Gemini Google Search grounding for product, competitor, and review research.',
      },
      'not-found': {
        title: 'Page Not Found | MAVYN',
        description: 'This page is not part of the MAVYN skincare intelligence demo.',
      },
    }[route.name]

    document.title = metadata.title
    const description = document.querySelector('meta[name="description"]')
    if (description) description.setAttribute('content', metadata.description)
  }, [route.name])

  useEffect(() => {
    function handlePopState() {
      setLocation(`${window.location.pathname}${window.location.search}`)
      window.scrollTo({ top: 0, behavior: 'auto' })
    }
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  const navigate = useCallback((to) => {
    const next = new URL(to, window.location.origin)
    window.history.pushState({}, '', `${next.pathname}${next.search}${next.hash}`)
    setLocation(`${next.pathname}${next.search}`)
    window.scrollTo({ top: 0, behavior: 'auto' })
  }, [])

  let page
  if (route.name === 'home') page = <HomePage navigate={navigate} />
  else if (route.name === 'catalog') page = <ProductCatalogPage navigate={navigate} />
  else if (route.name === 'product') {
    page = <ProductIntelligencePage key={route.productId} productId={route.productId} navigate={navigate} />
  } else if (route.name === 'studio') {
    page = <CreativeStudioPage key={location} />
  } else if (route.name === 'methodology') page = <MethodologyPage />
  else page = <NotFoundPage navigate={navigate} />

  const catalogActive = route.name === 'catalog' || route.name === 'product'

  return (
    <div className="app-shell">
      <header className="topbar app-topbar">
        <AppLink className="brand" to="/" navigate={navigate} aria-label="MAVYN overview">
          <span className="brand-mark">
            <img src="/mavyn.svg" alt="" width="48" height="48" />
          </span>
          <span>MAVYN<span className="brand-period">.</span></span>
        </AppLink>
        <nav className="site-nav" aria-label="Main navigation">
          <AppLink to="/" navigate={navigate} aria-current={route.name === 'home' ? 'page' : undefined}>Overview</AppLink>
          <AppLink to="/products" navigate={navigate} aria-current={catalogActive ? 'page' : undefined}>Product catalog</AppLink>
          <AppLink to="/studio" navigate={navigate} aria-current={route.name === 'studio' ? 'page' : undefined}>Creative studio</AppLink>
          <AppLink to="/methodology" navigate={navigate} aria-current={route.name === 'methodology' ? 'page' : undefined}>Data &amp; method</AppLink>
        </nav>
        <div
          className={`api-status ${apiState.status === 'online' ? 'is-online' : apiState.status === 'offline' ? 'is-offline' : ''}`}
          role="status"
          title={apiState.error || 'Backend connection status'}
        >
          <span className="status-dot" aria-hidden="true" />
          {apiState.status === 'online' ? 'API connected' : apiState.status === 'offline' ? 'API unavailable' : 'Connecting'}
        </div>
      </header>

      <main className="main-content" id="main-content">
        <Suspense fallback={<div className="route-page empty-state" role="status">Loading page</div>}>
          {page}
        </Suspense>
      </main>

      <footer className="footer app-footer">
        <span>MAVYN · Sample data unless a source is stated otherwise</span>
        <a href="/api/docs" target="_blank" rel="noreferrer">
          Backend API docs <ArrowUpRight size={14} aria-hidden="true" />
        </a>
      </footer>
    </div>
  )
}
