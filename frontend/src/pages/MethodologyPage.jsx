export default function MethodologyPage() {
  return (
    <div className="route-page methodology-page">
      <header className="page-heading">
        <p className="eyebrow">DATA &amp; METHOD</p>
        <h1>Research that shows its sources.</h1>
        <p className="page-lead">
          MAVYN uses Gemini with Google Search grounding for product, competitor, and public
          review research, then keeps unknown facts visibly unknown.
        </p>
      </header>

      <section className="methodology-grid">
        <article className="methodology-card">
          <h2>Products and competitors</h2>
          <p>
            Gemini searches public product pages and reputable Indian retailers. Returned records
            include clickable Google Search citations. Prices, ratings, review counts, and
            ingredients are left unavailable when a source does not support them.
          </p>
        </article>
        <article className="methodology-card">
          <h2>Customer feedback</h2>
          <p>
            Only short public review excerpts returned with citations are analyzed. Sentiment and
            themes use a lightweight keyword-based heuristic; a small set of excerpts is not
            representative of all customers.
          </p>
        </article>
        <article className="methodology-card">
          <h2>Freshness and availability</h2>
          <p>
            Research results are cached for up to six hours to reduce repeated searches. When
            Gemini or Google Search is unavailable, MAVYN reports the error rather than showing
            static product or review records.
          </p>
        </article>
        <article className="methodology-card">
          <h2>Sales opportunity</h2>
          <p>
            Public search results do not provide dated sell-through history. MAVYN therefore
            leaves the numerical forecast empty instead of treating review counts as sales.
          </p>
        </article>
        <article className="methodology-card">
          <h2>Generated content</h2>
          <p>
            Gemini creates campaign drafts from the retrieved product, competitor, and review
            evidence. Drafts are not verified claims; check product specifications, substantiation,
            and citations before publication.
          </p>
        </article>
      </section>
    </div>
  )
}
