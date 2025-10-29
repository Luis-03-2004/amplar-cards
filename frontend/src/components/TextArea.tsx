import '../App.css'

type Props = {
  label: string
  value: string
  onChange: (value: string) => void
  rows?: number
  placeholder?: string
}

export function TextArea({ label, value, onChange, rows = 8, placeholder }: Props) {
  return (
    <div className="input-section">
      <label htmlFor="coordenadas">{label}</label>
      <textarea
        id="coordenadas"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        rows={rows}
      />
    </div>
  )
}


