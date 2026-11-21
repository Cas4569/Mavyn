import { useLayoutEffect, useRef } from 'react'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

export default function AnimatedContent({ children, className = '' }) {
  const contentRef = useRef(null)

  useLayoutEffect(() => {
    const element = contentRef.current
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (!element || reduceMotion) return undefined

    const context = gsap.context(() => {
      gsap.fromTo(
        element,
        { autoAlpha: 0, y: 10 },
        {
          autoAlpha: 1,
          y: 0,
          duration: 0.4,
          ease: 'power2.out',
          clearProps: 'opacity,visibility,transform',
          scrollTrigger: {
            trigger: element,
            start: 'top 92%',
            once: true,
          },
        },
      )
    }, contentRef)

    return () => context.revert()
  }, [])

  return <div ref={contentRef} className={className}>{children}</div>
}
