import { Link, useLocation } from 'react-router-dom'
import '../App.css'

export function Header() {
  const location = useLocation()
  return (
    <header className="header">
      <div className="header-inner">
        <span className="brand">Amplar Tools</span>
        <nav className="nav">
          <Link className={location.pathname === '/' ? 'nav-link active' : 'nav-link'} to="/">Converter UTM</Link>
          <Link className={location.pathname === '/templates' ? 'nav-link active' : 'nav-link'} to="/templates">Templates</Link>
          <a className="nav-link" href="https://licenciamento.amplargs.com.br/" target="_blank" rel="noopener noreferrer">Licenciamento</a>
        </nav>
      </div>
    </header>
  )
}


