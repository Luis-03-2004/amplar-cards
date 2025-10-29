import { useState } from 'react'
import type { UTMResult } from './ResultsTable'
import '../App.css'

type Props = { results: UTMResult[] }

export function CopyButton({ results }: Props) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    if (!results.length) return
    const formatted = results
      .map(r => {
        const y = typeof r.utm_y === 'number' ? r.utm_y.toFixed(2) : String(r.utm_y)
        const x = typeof r.utm_x === 'number' ? r.utm_x.toFixed(2) : String(r.utm_x)
        return `${y} ${x}`
      })
      .join('\n')

    try {
      await navigator.clipboard.writeText(formatted)
      setCopied(true)
      setTimeout(() => setCopied(false), 800)
    } catch {
      alert('Erro ao copiar para a área de transferência')
    }
  }

  if (!results.length) return null

  return (
    <button onClick={handleCopy} className="btn-copy" title="Copiar: UTM Y UTM X">
      {copied ? '✓ Copiado!' : 'Copiar'}
    </button>
  )
}


