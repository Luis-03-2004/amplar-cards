import { useState } from 'react'
import './App.css'

interface UTMResult {
  utm_y: number
  utm_x: number
}

function App() {
  const [textoUsuario, setTextoUsuario] = useState('')
  const [results, setResults] = useState<UTMResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

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
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          texto_do_usuario: textoUsuario,
        }),
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

  const handleCopyResults = async () => {
    if (results.length === 0) return

    // Formata como "utm_y utm_x" por linha
    const formattedText = results
      .map(result => `${result.utm_y.toFixed(2)} ${result.utm_x.toFixed(2)}`)
      .join('\n')

    try {
      await navigator.clipboard.writeText(formattedText)
      setCopied(true)
      setTimeout(() => setCopied(false), 500)
    } catch {
      alert('Erro ao copiar para a área de transferência')
    }
  }

  return (
    <div className="app">
      <div className="container">
        <h1>Conversor de Coordenadas para UTM</h1>
        
        <div className="input-section">
          <label htmlFor="coordenadas">
            Cole suas coordenadas aqui (formato: longitude latitude, uma por linha):
          </label>
          <textarea
            id="coordenadas"
            value={textoUsuario}
            onChange={(e) => setTextoUsuario(e.target.value)}
            placeholder="Exemplo:&#10;-46.5658 -21.7892&#10;-43.2096 -22.9035&#10;-46.6333 -23.5505"
            rows={8}
          />
        </div>

        <div className="buttons">
          <button 
            onClick={() => handleConvert()} 
            disabled={loading}
            className="btn-primary"
          >
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
              <button 
                onClick={handleCopyResults}
                className="btn-copy"
                title="Copiar resultados no formato: UTM Y UTM X"
              >
                {copied ? '✓ Copiado!' : 'Copiar'}
              </button>
            </div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>UTM Y</th>
                    <th>UTM X</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((result, index) => (
                    <tr key={index}>
                      <td>{result.utm_y.toFixed(2)}</td>
                      <td>{result.utm_x.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
