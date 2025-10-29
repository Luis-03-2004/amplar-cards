import { useState } from 'react'
import { TextArea } from '../components/TextArea'
import { ResultsTable, type UTMResult } from '../components/ResultsTable'
import { CopyButton } from '../components/CopyButton'
import '../App.css'

export function ConvertPage() {
  const [textoUsuario, setTextoUsuario] = useState('')
  const [results, setResults] = useState<UTMResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleConvert = async () => {
    if (!textoUsuario.trim()) {
      setError('Por favor, insira pelo menos uma coordenada')
      return
    }
    setLoading(true)
    setError(null)
    setResults([])
    try {
      const response = await fetch('http://localhost:5000/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texto_do_usuario: textoUsuario }),
      })
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Erro ao processar coordenadas')
      }
      const data = await response.json()
      setResults(data.items || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Conversor de Coordenadas para UTM</h1>

      <TextArea
        label="Cole suas coordenadas aqui (formato: longitude latitude, uma por linha):"
        value={textoUsuario}
        onChange={setTextoUsuario}
        rows={8}
        placeholder={'Exemplo:\n-46.5658 -21.7892\n-43.2096 -22.9035\n-46.6333 -23.5505'}
      />

      <div className="buttons">
        <button onClick={handleConvert} disabled={loading} className="btn-primary">
          {loading ? 'Processando...' : 'Converter Coordenadas para UTM'}
        </button>
      </div>

      {error && (
        <div className="error">
          <strong>Erro:</strong> {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="results">
          <div className="results-header">
            <h2>Resultados ({results.length} coordenadas convertidas)</h2>
            <CopyButton results={results} />
          </div>
          <ResultsTable results={results} />
        </div>
      )}
    </div>
  )
}


