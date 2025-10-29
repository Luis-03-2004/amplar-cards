import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import './App.css'
import { Header } from './components/Header'
import { ConvertPage } from './pages/ConvertPage'
import { TemplatesPage } from './pages/TemplatesPage'

function App() {
  function ExternalRedirect() {
    useEffect(() => {
      window.location.href = 'https://licenciamento.amplargs.com.br/'
    }, [])
    return null
  }
  return (
    <div className="app">
      <BrowserRouter>
        <Header />
        <Routes>
          <Route path="/" element={<ConvertPage />} />
          <Route path="/templates" element={<TemplatesPage />} />
          <Route path="/licenciamento" element={<ExternalRedirect />} />
        </Routes>
      </BrowserRouter>
    </div>
  )
}

export default App
