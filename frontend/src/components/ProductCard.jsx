import { useState } from 'react'
import { Package, Star } from 'lucide-react'
import AppLink from './AppLink.jsx'

const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
})

const productImages = {
  'dk-sun-001': '/product-images/watermelon-cooling-sunscreen.png',
  'dk-ser-001': '/product-images/vitamin-c-e-super-bright-serum.png',
  'dk-ser-002': '/product-images/niacinamide-spot-reduction-serum.png',
  'dk-moist-001': '/product-images/ceramide-barrier-repair-moisturizer.png',
  'dk-moist-002': '/product-images/strawberry-dew-strobe-cream.png',
  'dk-clean-001': '/product-images/cica-gentle-cleanser.png',
  'dk-clean-002': '/product-images/vitamin-c-brightening-face-wash.png',
  'dk-toner-001': '/product-images/rice-water-brightening-toner.png',
}

const productImageMatches = [
  [['vitamin c', 'face wash'], '/product-images/vitamin-c-brightening-face-wash.png'],
  [['watermelon', 'sunscreen'], '/product-images/watermelon-cooling-sunscreen.png'],
  [['vitamin c', 'serum'], '/product-images/vitamin-c-e-super-bright-serum.png'],
  [['niacinamide', 'serum'], '/product-images/niacinamide-spot-reduction-serum.png'],
  [['ceramide', 'moisturizer'], '/product-images/ceramide-barrier-repair-moisturizer.png'],
  [['strawberry', 'cream'], '/product-images/strawberry-dew-strobe-cream.png'],
  [['cica', 'cleanser'], '/product-images/cica-gentle-cleanser.png'],
  [['rice water', 'toner'], '/product-images/rice-water-brightening-toner.png'],
]

function ProductArtwork({ product }) {
  const [imageFailed, setImageFailed] = useState(false)
  const productName = product.name.toLowerCase()
  const matchedImage = productImageMatches.find(([terms]) =>
    terms.every((term) => productName.includes(term)),
  )?.[1]
  const imageSrc = productImages[product.id] || matchedImage || product.hero_image

  if (!imageSrc || imageFailed) {
    return (
      <div className="product-artwork product-artwork-fallback" aria-hidden="true">
        <Package size={34} strokeWidth={1.4} />
      </div>
    )
  }

  return (
    <img
      className="product-artwork"
      src={imageSrc}
      alt={product.name}
      loading="lazy"
      onError={() => setImageFailed(true)}
    />
  )
}

export default function ProductCard({ product, categoryName, navigate }) {
  return (
    <AppLink
      className="product-card product-card-link"
      to={`/products/${encodeURIComponent(product.id)}`}
      navigate={navigate}
    >
      <div className="product-image-wrap">
        <ProductArtwork product={product} />
        <span className="product-source">LIVE SEARCH</span>
      </div>
      <div className="product-card-body">
        <span className="product-category">{categoryName}</span>
        <h2>{product.name}</h2>
        <p className="product-tagline">{product.tagline || 'Product details and market signals'}</p>
        <div className="product-card-meta">
          <strong>{product.price_inr == null ? 'Price unavailable' : currency.format(product.price_inr)}</strong>
          <span>
            <Star size={14} aria-hidden="true" />
            {product.rating == null ? 'Rating unavailable' : ` ${product.rating.toFixed(1)}`}
          </span>
        </div>
      </div>
    </AppLink>
  )
}

export { ProductArtwork }
