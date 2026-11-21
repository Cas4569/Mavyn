export default function ResearchSources({ sources = [], fetchedAt }) {
  if (!sources.length) {
    return <p className="research-source-note">No source links were returned for this research.</p>
  }

  return (
    <details className="research-sources">
      <summary>Google Search sources ({sources.length})</summary>
      <ul>
        {sources.map((source) => (
          <li key={source.url}>
            <a href={source.url} target="_blank" rel="noreferrer">
              {source.title || source.url}
            </a>
          </li>
        ))}
      </ul>
      {fetchedAt && <small>Research fetched {new Date(fetchedAt).toLocaleString()}</small>}
    </details>
  )
}
