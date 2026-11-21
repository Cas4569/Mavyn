import { useEffect } from 'react'

export default function SmoothScroll({ children }) {
  useEffect(() => {
    const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)')
    let lenis
    let gsap
    let scrollTrigger
    let tick
    let idleId
    let timeoutId
    let scheduled = false
    let disposed = false

    function stop() {
      if (!lenis) return
      lenis.off('scroll', scrollTrigger.update)
      gsap.ticker.remove(tick)
      lenis.destroy()
      gsap.ticker.lagSmoothing(500, 33)
      lenis = undefined
      gsap = undefined
      scrollTrigger = undefined
      tick = undefined
    }

    async function start() {
      if (motionPreference.matches || lenis || disposed) return
      try {
        const [lenisModule, gsapModule, scrollTriggerModule] = await Promise.all([
          import('lenis'),
          import('gsap'),
          import('gsap/ScrollTrigger'),
        ])
        if (motionPreference.matches || disposed) return
        const Lenis = lenisModule.default
        gsap = gsapModule.gsap
        scrollTrigger = scrollTriggerModule.ScrollTrigger
        gsap.registerPlugin(scrollTrigger)
        lenis = new Lenis({ smoothWheel: true, anchors: true })
        lenis.on('scroll', scrollTrigger.update)
        tick = (time) => lenis?.raf(time * 1000)
        gsap.ticker.add(tick)
        gsap.ticker.lagSmoothing(0)
      } catch (error) {
        console.error('Smooth scrolling could not be initialized.', error)
      }
    }

    function scheduleStart() {
      if (motionPreference.matches || lenis || scheduled || disposed) return
      scheduled = true
      if ('requestIdleCallback' in window) {
        idleId = window.requestIdleCallback(() => {
          scheduled = false
          void start()
        }, { timeout: 5000 })
      } else {
        timeoutId = window.setTimeout(() => {
          scheduled = false
          void start()
        }, 1500)
      }
    }

    function updateMotionPreference() {
      if (motionPreference.matches) {
        if (idleId !== undefined) window.cancelIdleCallback(idleId)
        if (timeoutId !== undefined) window.clearTimeout(timeoutId)
        scheduled = false
        stop()
      } else {
        scheduleStart()
      }
    }

    function onPageLoad() {
      scheduleStart()
    }

    if (document.readyState === 'complete') onPageLoad()
    else window.addEventListener('load', onPageLoad, { once: true })
    motionPreference.addEventListener('change', updateMotionPreference)

    return () => {
      disposed = true
      window.removeEventListener('load', onPageLoad)
      motionPreference.removeEventListener('change', updateMotionPreference)
      if (idleId !== undefined) window.cancelIdleCallback(idleId)
      if (timeoutId !== undefined) window.clearTimeout(timeoutId)
      stop()
    }
  }, [])

  return children
}
