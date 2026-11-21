export default function AppLink({ to, navigate, children, onClick, ...props }) {
  function handleClick(event) {
    onClick?.(event)
    if (
      event.defaultPrevented
      || event.button !== 0
      || event.metaKey
      || event.ctrlKey
      || event.shiftKey
      || event.altKey
      || props.target
      || props.download
    ) {
      return
    }

    event.preventDefault()
    navigate(to)
  }

  return <a href={to} {...props} onClick={handleClick}>{children}</a>
}
