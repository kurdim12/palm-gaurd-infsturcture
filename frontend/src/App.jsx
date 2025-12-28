import React, { useState, useEffect } from 'react'
import './App.css'
import {
  getLatestReading,
  getLatestAlerts,
  getSimulatorStatus,
  startSimulator,
  stopSimulator,
  controlPump,
  doseNutrients,
  getRoboCraftReport,
  exportCSV
} from './services/api'

function App() {
  const [latest, setLatest] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [simulatorRunning, setSimulatorRunning] = useState(false)
  const [doseAmount, setDoseAmount] = useState(100)
  const [report, setReport] = useState(null)
  const [message, setMessage] = useState('')

  const fetchData = async () => {
    try {
      const [readingRes, alertsRes, simStatusRes] = await Promise.all([
        getLatestReading(),
        getLatestAlerts(),
        getSimulatorStatus()
      ])
      setLatest(readingRes.data)
      setAlerts(alertsRes.data)
      setSimulatorRunning(simStatusRes.data.running)
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 3000)
    return () => clearInterval(interval)
  }, [])

  const toggleSimulator = async () => {
    try {
      if (simulatorRunning) {
        await stopSimulator()
      } else {
        await startSimulator()
      }
      fetchData()
    } catch (error) {
      console.error('Error toggling simulator:', error)
    }
  }

  const handlePumpControl = async (state) => {
    if (!window.confirm(`Turn pump ${state}?`)) return
    try {
      await controlPump(state)
      showMessage(`Pump turned ${state}`)
      fetchData()
    } catch (error) {
      showMessage('Error controlling pump')
    }
  }

  const handleDose = async () => {
    if (!window.confirm(`Add ${doseAmount}ml of nutrients?`)) return
    try {
      await doseNutrients(doseAmount)
      showMessage(`Dosed ${doseAmount}ml successfully`)
      fetchData()
    } catch (error) {
      showMessage('Error dosing nutrients')
    }
  }

  const generateReport = async () => {
    try {
      const response = await getRoboCraftReport()
      setReport(response.data)
    } catch (error) {
      console.error('Error generating report:', error)
    }
  }

  const showMessage = (msg) => {
    setMessage(msg)
    setTimeout(() => setMessage(''), 3000)
  }

  const getTDSStatus = (tds) => {
    if (!tds) return 'text-gray-600'
    if (tds < 500 || tds > 1100) return 'text-danger'
    if (tds < 600 || tds > 1000) return 'text-warning'
    return 'text-primary'
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <nav className="bg-white shadow-lg mb-8">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-primary">🌱 DualFarm</h1>
              <span className="demo-badge">DEMO MODE</span>
            </div>
            <button onClick={toggleSimulator} className={`btn ${simulatorRunning ? 'btn-danger' : 'btn-primary'}`}>
              {simulatorRunning ? '⏸ Stop Simulation' : '▶ Start Simulation'}
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4">
        {message && (
          <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
            {message}
          </div>
        )}

        {/* System Status */}
        <div className="card mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">System Status</h2>
              <p className="text-sm text-gray-500">
                {latest ? new Date(latest.timestamp).toLocaleString() : 'No data'}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <span className={`status-indicator ${latest?.pump_state === 'ON' ? 'status-on' : 'status-off'}`}></span>
                <span className="text-sm font-medium">Pump {latest?.pump_state || 'OFF'}</span>
              </div>
              <div className="flex items-center">
                <span className={`status-indicator ${simulatorRunning ? 'status-on' : 'status-off'}`}></span>
                <span className="text-sm font-medium">Simulator {simulatorRunning ? 'ON' : 'OFF'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="card">
            <p className="text-sm text-gray-500 font-medium">TDS (Nutrients)</p>
            <div className="mt-2 flex items-baseline">
              <p className={`text-3xl font-bold ${getTDSStatus(latest?.tds_ppm)}`}>
                {latest?.tds_ppm.toFixed(1) || '0'}
              </p>
              <span className="ml-2 text-lg text-gray-500">ppm</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">Target: 500-1100 ppm</p>
          </div>

          <div className="card">
            <p className="text-sm text-gray-500 font-medium">Temperature</p>
            <div className="mt-2 flex items-baseline">
              <p className="text-3xl font-bold text-secondary">
                {latest?.temperature_c.toFixed(1) || '0'}
              </p>
              <span className="ml-2 text-lg text-gray-500">°C</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">Target: 15-35°C</p>
          </div>

          <div className="card">
            <p className="text-sm text-gray-500 font-medium">Water Level</p>
            <div className="mt-2 flex items-baseline">
              <p className="text-3xl font-bold text-warning">
                {latest?.water_level_cm.toFixed(1) || '0'}
              </p>
              <span className="ml-2 text-lg text-gray-500">cm</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">Minimum: 10 cm</p>
          </div>

          <div className="card">
            <p className="text-sm text-gray-500 font-medium">Active Alerts</p>
            <div className="mt-2 flex items-baseline">
              <p className="text-3xl font-bold text-danger">{alerts.length}</p>
              <span className="ml-2 text-lg text-gray-500">alerts</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              {alerts.length === 0 ? 'All normal' : 'Attention required'}
            </p>
          </div>
        </div>

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="card mb-6">
            <h2 className="text-xl font-semibold mb-4">⚠️ Active Alerts</h2>
            <div className="space-y-3">
              {alerts.map(alert => (
                <div key={alert.id} className={`p-4 rounded border-l-4 ${
                  alert.severity === 'critical' ? 'bg-red-50 border-red-500' : 'bg-yellow-50 border-yellow-500'
                }`}>
                  <p className="font-semibold">{alert.alert_type.replace(/_/g, ' ').toUpperCase()}</p>
                  <p className="text-sm mt-1">{alert.message}</p>
                  <p className="text-xs mt-2 opacity-75">{new Date(alert.timestamp).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Controls */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Pump Control</h2>
            <div className="flex space-x-4">
              <button onClick={() => handlePumpControl('ON')} className="btn btn-primary flex-1">
                Turn ON
              </button>
              <button onClick={() => handlePumpControl('OFF')} className="btn btn-danger flex-1">
                Turn OFF
              </button>
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Nutrient Dosing</h2>
            <div className="flex space-x-4">
              <input
                type="number"
                min="10"
                max="1000"
                step="10"
                value={doseAmount}
                onChange={(e) => setDoseAmount(Number(e.target.value))}
                className="flex-1 px-4 py-2 border rounded"
                placeholder="Amount (ml)"
              />
              <button onClick={handleDose} className="btn btn-secondary">
                Dose
              </button>
            </div>
          </div>
        </div>

        {/* Reports */}
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">📊 Reports & Export</h2>
          <div className="flex space-x-4">
            <button onClick={generateReport} className="btn btn-primary">
              Generate RoboCraft Report
            </button>
            <button onClick={exportCSV} className="btn btn-secondary">
              Export CSV
            </button>
          </div>
          {report && (
            <div className="mt-4 p-4 bg-gray-50 rounded max-h-96 overflow-y-auto">
              <pre className="text-sm whitespace-pre-wrap">{report.report_markdown}</pre>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="card mb-8">
          <h3 className="font-semibold mb-2">ℹ️ Quick Start</h3>
          <ol className="text-sm text-gray-700 space-y-1 list-decimal list-inside">
            <li>Click "Start Simulation" to begin generating sensor data</li>
            <li>Monitor TDS, Temperature, and Water Level in real-time</li>
            <li>Alerts will appear automatically when thresholds are exceeded</li>
            <li>Use controls to operate pump and dose nutrients</li>
            <li>Generate report for RoboCraft competition submission</li>
          </ol>
        </div>
      </div>
    </div>
  )
}

export default App
