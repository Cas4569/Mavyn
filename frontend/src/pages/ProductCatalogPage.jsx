import { useEffect, useMemo, useState } from 'react'
import { CircleAlert, Droplets, FlaskConical, Leaf, LoaderCircle, Search, Sun, Waves } from 'lucide-react'
import { api } from '../api.js'
import ProductCard from '../components/ProductCard.jsx'
import ResearchSources from '../components/ResearchSources.jsx'

const categoryIcons = {
  sunscreens: Sun,
  serums: FlaskConical,
  moisturizers: Droplets,
  cleansers: Waves,
  toners: Leaf,
}

export default function ProductCatalogPage({ navigate }) {
  const [categories, setCategories] = useState([])
  const [products, setProducts] = useState([])
  const [research, setResearch] = useState({ sources: [], fetchedAt: null })
  const [categoryId, setCategoryId] = useState('all')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    Promise.all([api.categories(), api.dotAndKeyProducts()])
      .then(([categoryResult, productResult]) => {
        if (!Array.isArray(categoryResult.categories) || !Array.isArray(productResult.products)) {
          throw new Error('The backend returned an invalid catalog response.')
        }
        if (!active) return
        setCategories(categoryResult.categories)
        setProducts(productResult.products)
        setResearch({
          sources: productResult.sources || [],
          fetchedAt: productResult.fetched_at || null,
        })
      })
      .catch((requestError) => {
        if (active) setError(requestError.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const categoryNames = useMemo(
    () => Object.fromEntries(categories.map((category) => [category.id, category.name])),
    [categories],
  )
  const visibleProducts = useMemo(() => {
    const query = search.trim().toLowerCase()
    return products.filter((product) => {
      const matchesCategory = categoryId === 'all' || product.category_id === categoryId
      const matchesSearch = !query || product.name.toLowerCase().includes(query)
      return matchesCategory && matchesSearch
    })
  }, [categoryId, products, search])

  return (
    <div className="route-page catalog-page">
      <header className="page-heading">
        <p className="eyebrow">DOT &amp; KEY / PORTFOLIO</p>
        <h1>Product catalog</h1>
        <p className="page-lead">
          Select a product to inspect current Google Search-grounded product records, competitors,
          customer feedback, and market opportunities.
        </p>
      </header>

      <section aria-label="Product catalog">
        <div className="catalog-controls">
          <div className="catalog-filters" aria-label="Filter by category">
            <button
              className={`category-button ${categoryId === 'all' ? 'active' : ''}`}
              type="button"
              onClick={() => setCategoryId('all')}
              aria-pressed={categoryId === 'all'}
            >
              All products
            </button>
            {categories.map((category) => {
              const CategoryIcon = categoryIcons[category.id]
              return (
                <button
                  className={`category-button ${category.id === categoryId ? 'active' : ''}`}
                  key={category.id}
                  type="button"
                  onClick={() => setCategoryId(category.id)}
                  aria-pressed={category.id === categoryId}
                >
                  {CategoryIcon && <CategoryIcon size={16} aria-hidden="true" />}
                  {category.name}
                </button>
              )
            })}
          </div>
          <label className="search-box catalog-search">
            <Search size={16} aria-hidden="true" />
            <input
              aria-label="Search Dot & Key products"
              placeholder="Search products"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </label>
        </div>

        {loading && (
          <div className="empty-state" role="status">
            <LoaderCircle className="spin" size={20} aria-hidden="true" /> Loading catalog
          </div>
        )}
        {error && <div className="notice notice-error" role="alert"><CircleAlert size={18} />{error}</div>}
        {!loading && !error && (
          <>
            <p className="catalog-result-count">
              {visibleProducts.length} {visibleProducts.length === 1 ? 'product' : 'products'}
              {categoryId !== 'all' ? ` in ${categoryNames[categoryId]}` : ''}
              <span>Live Google Search research</span>
            </p>
            <ResearchSources sources={research.sources} fetchedAt={research.fetchedAt} />
            {visibleProducts.length > 0 ? (
              <div className="product-grid">
                {visibleProducts.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    categoryName={categoryNames[product.category_id] || product.category_id}
                    navigate={navigate}
                  />
                ))}
              </div>
            ) : (
              <p className="empty-state">
                {products.length ? 'No products match these filters.' : 'No products are available.'}
              </p>
            )}
          </>
        )}
      </section>
    </div>
  )
}
