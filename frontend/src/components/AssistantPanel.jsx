import React, { useState } from 'react'
import { api } from '../api'

export default function AssistantPanel({ summary }) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState(null)

  const ask = async () => {
    setLoading(true)
    setError(null)
    try {
      // Backend zaten grafik_analiz.get_analysis_summary() çıktısını AI'a iletiyor
      const { data } = await api.get('/ask-ai')
      setMessage(data?.message || '')
    } catch (e) {
      setError(e?.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <h2 className="font-semibold">🤖 AI Finans Asistanı</h2>
        <button onClick={ask} className="btn-primary text-sm" disabled={loading}>
          {loading ? 'Analiz...' : 'Yorumu Yenile'}
        </button>
      </div>

      <div className="text-xs text-gray-500 mb-3">
        Firestore verilerinden üretilen özet analizi inceleyip kısa bir yorum üretir.
      </div>

      <div className="grid grid-cols-2 gap-2 text-sm mb-3">
        <MiniStat label="Toplam Gelir" value={summary?.toplam_gelir ?? 0} color="text-green-600" />
        <MiniStat label="Toplam Gider" value={summary?.toplam_gider ?? 0} color="text-red-600" />
        <MiniStat label="Tahmin Gelir" value={summary?.tahmin?.gelir ?? 0} />
        <MiniStat label="Tahmin Gider" value={summary?.tahmin?.gider ?? 0} />
      </div>

      <div className="text-sm whitespace-pre-wrap flex-1 overflow-auto border rounded p-3 bg-gray-50">
        {loading ? 'Düşünüyorum… ⏳' : (message || 'Yorum için sağ üstten butona tıklayın.')}
      </div>

      {error && <div className="text-xs text-red-600 mt-2">{String(error)}</div>}
    </div>
  )
}

function MiniStat({ label, value, color = 'text-gray-900' }) {
  return (
    <div className="bg-gray-50 rounded p-2">
      <div className="text-gray-500">{label}</div>
      <div className={`font-semibold ${color}`}>{value}</div>
    </div>
  )
}
