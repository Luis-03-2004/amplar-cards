import '../App.css'

export type UTMResult = { utm_y: number | string; utm_x: number | string }

type Props = { results: UTMResult[] }

export function ResultsTable({ results }: Props) {
  if (results.length === 0) return null
  return (
    <div className="results">
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>UTM Y</th>
              <th>UTM X</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={i}>
                <td>{typeof r.utm_y === 'number' ? r.utm_y.toFixed(2) : String(r.utm_y)}</td>
                <td>{typeof r.utm_x === 'number' ? r.utm_x.toFixed(2) : String(r.utm_x)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


