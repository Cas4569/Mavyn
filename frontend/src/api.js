const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'
const CATALOG_CACHE_TTL_MS = 6 * 60 * 60 * 1000

let catalogCache
let catalogCacheExpiresAt = 0
let catalogRequest

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  let payload
  try {
    payload = await response.json()
  } catch {
    throw new Error(`The backend returned an invalid response (${response.status}).`)
  }

  if (!response.ok) {
    throw new Error(payload.detail || `The request failed (${response.status}).`)
  }

  return payload
}

function dotAndKeyProducts() {
  if (catalogCache && Date.now() < catalogCacheExpiresAt) {
    return Promise.resolve(catalogCache)
  }
  if (!catalogRequest) {
    catalogRequest = request('/products/dot-and-key')
      .then((result) => {
        catalogCache = result
        catalogCacheExpiresAt = Date.now() + CATALOG_CACHE_TTL_MS
        return result
      })
      .finally(() => {
        catalogRequest = undefined
      })
  }
  return catalogRequest
}

export const api = {
  health: () => request('/health'),
  categories: () => request('/categories'),
  products: (categoryId) => request(`/products?category=${encodeURIComponent(categoryId)}`),
  dotAndKeyProducts,
  product: (productId) => request(`/products/${encodeURIComponent(productId)}`),
  productComparison: (productId) =>
    request(`/products/${encodeURIComponent(productId)}/comparison`),
  productStrategy: (productId) =>
    request(`/products/${encodeURIComponent(productId)}/strategy`),
  analyzeReviews: (productId) =>
    request('/reviews/analyze', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId }),
    }),
  generateContent: (productId) =>
    request('/content/generate', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, provider: 'gemini' }),
    }),
}
