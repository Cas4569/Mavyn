const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

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

export const api = {
  health: () => request('/health'),
  categories: () => request('/categories'),
  products: (categoryId) => request(`/products?category=${encodeURIComponent(categoryId)}`),
  dotAndKeyProducts: () => request('/products/dot-and-key'),
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
