import { useEffect, useRef } from 'react'

const VoiceWave = ({ isActive = false, className = '' }) => {
  const canvasRef = useRef(null)
  const animationRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    const width = canvas.width
    const height = canvas.height
    let animationId

    if (isActive) {
      let phase = 0
      const bars = 20
      const barWidth = width / bars

      const draw = () => {
        ctx.clearRect(0, 0, width, height)
        ctx.fillStyle = '#0EA5E9'

        for (let i = 0; i < bars; i++) {
          const barHeight = Math.sin(phase + i * 0.3) * (height / 2) + height / 2
          const x = i * barWidth
          const y = (height - barHeight) / 2

          ctx.fillRect(x, y, barWidth - 2, barHeight)
        }

        phase += 0.1
        animationId = requestAnimationFrame(draw)
      }

      draw()
    } else {
      ctx.clearRect(0, 0, width, height)
    }

    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId)
      }
    }
  }, [isActive])

  return (
    <canvas
      ref={canvasRef}
      width={200}
      height={60}
      className={className}
    />
  )
}

export default VoiceWave

