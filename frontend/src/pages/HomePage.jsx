import { ArrowRight, BarChart3, MessageSquareText, Sparkles } from 'lucide-react'
import AppLink from '../components/AppLink.jsx'

const workflow = [
  {
    number: '01',
    icon: BarChart3,
    title: 'Choose a product',
    description: 'Search current public product listings and open a sourced product workspace.',
  },
  {
    number: '02',
    icon: MessageSquareText,
    title: 'Review the evidence',
    description: 'Compare cited competitors and surface review themes, gaps, and next steps.',
  },
  {
    number: '03',
    icon: Sparkles,
    title: 'Build a campaign draft',
    description: 'Turn grounded product and review signals into content to refine with your team.',
  },
]

export default function HomePage({ navigate }) {
  return (
    <div className="route-page home-page">
      <section className="home-hero">
        <p className="eyebrow">MAVYN / DOT &amp; KEY MARKET INTELLIGENCE</p>
        <h1>From product signals<br />to campaign drafts.</h1>
        <p className="page-lead">
          Explore a skincare product, compare its live market set, and turn customer-feedback
          signals into a campaign starting point.
        </p>
        <div className="page-actions">
          <AppLink className="primary-button" to="/products" navigate={navigate}>
            Browse products <ArrowRight size={16} aria-hidden="true" />
          </AppLink>
          <AppLink className="text-link" to="/methodology" navigate={navigate}>
            See data and method
          </AppLink>
        </div>
        <p className="research-disclosure">Research is grounded in Google Search and cached for up to six hours.</p>
      </section>

      <section className="home-workflow" aria-labelledby="workflow-title">
        <div className="page-heading">
          <p className="eyebrow">A THREE-STEP WORKFLOW</p>
          <h2 id="workflow-title">Research first. Create second.</h2>
        </div>
        <div className="workflow-grid">
          {workflow.map(({ number, icon: Icon, title, description }) => (
            <article className="workflow-step" key={number}>
              <div className="workflow-step-top">
                <span>{number}</span>
                <Icon size={19} aria-hidden="true" />
              </div>
              <h3>{title}</h3>
              <p>{description}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="home-note">
        <div>
          <p className="eyebrow">A NOTE ON THIS BUILD</p>
          <h2>Every market claim needs a source.</h2>
          <p>
            MAVYN shows Google Search citations for retrieved product, competitor, and review
            records. Missing facts stay unknown, and the app does not invent a sales forecast.
          </p>
        </div>
        <AppLink className="secondary-button" to="/methodology" navigate={navigate}>
          Read the methodology <ArrowRight size={15} aria-hidden="true" />
        </AppLink>
      </section>
    </div>
  )
}
