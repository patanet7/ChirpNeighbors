import { useState } from 'react';
import './App.css';

function App() {
  const [status, setStatus] = useState<string>('idle');

  const checkBackendHealth = async () => {
    try {
      setStatus('checking...');
      const response = await fetch('/api/health');
      const data = await response.json();
      setStatus(data.status === 'ok' ? 'Backend is healthy! 🎉' : 'Backend responded');
    } catch (error) {
      setStatus('Backend is not reachable. Please start the backend server.');
      console.error('Health check failed:', error);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🐦 ChirpNeighbors</h1>
        <p>Bird Sound Identification System</p>
      </header>

      <main className="App-main">
        <section className="card">
          <h2>Welcome to ChirpNeighbors</h2>
          <p>
            Upload bird sounds from your ESP32 device or web interface to identify bird species.
          </p>
        </section>

        <section className="card">
          <h3>Backend Status</h3>
          <button onClick={checkBackendHealth} className="button">
            Check Backend Health
          </button>
          {status !== 'idle' && <p className="status">{status}</p>}
        </section>

        <section className="card">
          <h3>Features</h3>
          <ul className="feature-list">
            <li>🎤 Audio Upload & Processing</li>
            <li>🤖 ML-powered Bird Identification</li>
            <li>📊 Real-time Analysis</li>
            <li>📱 ESP32 Integration</li>
          </ul>
        </section>
      </main>

      <footer className="App-footer">
        <p>Built with FastAPI + React + TypeScript</p>
      </footer>
    </div>
  );
}

export default App;
