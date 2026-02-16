import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import VideoDetail from './pages/VideoDetail'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/video/:id" element={<VideoDetail />} />
      </Routes>
    </Layout>
  )
}

export default App
