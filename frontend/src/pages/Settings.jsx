import React, { useState, useEffect } from 'react'
import { useTheme } from '../theme.jsx'
import { api } from '../api'

export default function Settings() {
  const { theme, setTheme, resetTheme } = useTheme()
  const [draft, setDraft] = useState(theme)
  const [budgetStatus, setBudgetStatus] = useState({ bakiye: 0, aylikLimit: 0, islemSayisi: 0 })
  const [limitInput, setLimitInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  const apply = (e) => {
    e.preventDefault()
    setTheme(draft)
  }

  const handleChange = (key, value) => setDraft((t) => ({ ...t, [key]: value }))

  const loadBudgetStatus = async () => {
    try {
      const { data } = await api.get('/budget-manager/status')
      setBudgetStatus(data)
      setLimitInput(data.aylikLimit || '')
    } catch (e) {
      console.error('Bütçe durumu yüklenemedi:', e)
    }
  }

  useEffect(() => {
    loadBudgetStatus()
  }, [])

  const handleSetLimit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')
    try {
      await api.put('/budget-manager/limit', { aylikLimit: parseFloat(limitInput) || 0 })
      setMessage('Aylık limit güncellendi!')
      await loadBudgetStatus()
    } catch (e) {
      setMessage('Hata: ' + (e?.response?.data?.detail || e.message))
    } finally {
      setLoading(false)
    }
  }

  const handleLoadHistory = async () => {
    setLoading(true)
    setMessage('')
    try {
      const { data } = await api.post('/budget-manager/load-history')
      setMessage(`Geçmiş veriler yüklendi: ${data.islemSayisi} işlem`)
      await loadBudgetStatus()
    } catch (e) {
      setMessage('Hata: ' + (e?.response?.data?.detail || e.message))
    } finally {
      setLoading(false)
    }
  }

  const handleSaveData = async () => {
    setLoading(true)
    setMessage('')
    try {
      await api.post('/budget-manager/save')
      setMessage('Veriler kaydedildi!')
    } catch (e) {
      setMessage('Hata: ' + (e?.response?.data?.detail || e.message))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Görünüm & Tema</h1>
          <p className="text-sm text-gray-600">Renkleri değiştirerek kendi temanı oluştur.</p>
        </div>
        <button onClick={resetTheme} className="btn-primary">Varsayılana dön</button>
      </div>

      <form onSubmit={apply} className="card p-5 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <ColorInput label="Ana Renk" value={draft.primary} onChange={(v) => handleChange('primary', v)} />
          <ColorInput label="Ana Renk (Koyu)" value={draft.primaryDark} onChange={(v) => handleChange('primaryDark', v)} />
          <ColorInput label="Vurgu Rengi" value={draft.accent} onChange={(v) => handleChange('accent', v)} />
          <ColorInput label="Yüzey" value={draft.surface} onChange={(v) => handleChange('surface', v)} />
          <ColorInput label="Arka Plan" value={draft.background} onChange={(v) => handleChange('background', v)} />
          <ColorInput label="Metin" value={draft.text} onChange={(v) => handleChange('text', v)} />
        </div>

        <div className="flex items-center gap-3">
          <button type="submit" className="btn-primary">Kaydet ve Uygula</button>
          <span className="text-sm text-gray-500">Değişiklikler anında yansır.</span>
        </div>
      </form>

      {/* Bütçe Yönetimi */}
      <div className="card p-5 space-y-4">
        <h2 className="text-xl font-semibold">Bütçe Yönetimi</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-sm text-gray-600">Güncel Bakiye</div>
            <div className={`text-2xl font-semibold ${budgetStatus.bakiye >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {budgetStatus.bakiye.toFixed(2)} TL
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-sm text-gray-600">Aylık Limit</div>
            <div className="text-2xl font-semibold text-indigo-600">
              {budgetStatus.aylikLimit.toFixed(2)} TL
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded">
            <div className="text-sm text-gray-600">Toplam İşlem</div>
            <div className="text-2xl font-semibold text-gray-700">
              {budgetStatus.islemSayisi}
            </div>
          </div>
        </div>

        {message && (
          <div className={`p-3 rounded text-sm ${message.includes('Hata') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'}`}>
            {message}
          </div>
        )}

        <form onSubmit={handleSetLimit} className="space-y-3">
          <label className="block text-sm space-y-1">
            <span className="text-gray-700">Aylık Limit Belirle (TL)</span>
            <div className="flex gap-2">
              <input
                type="number"
                value={limitInput}
                onChange={(e) => setLimitInput(e.target.value)}
                className="flex-1 border rounded px-3 py-2"
                placeholder="0"
                min="0"
                step="0.01"
              />
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Kaydediliyor...' : 'Limit Güncelle'}
              </button>
            </div>
          </label>
        </form>

        <div className="flex gap-2">
          <button
            onClick={handleLoadHistory}
            className="px-4 py-2 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 text-sm"
            disabled={loading}
          >
            📥 Geçmişi Yükle
          </button>
          <button
            onClick={handleSaveData}
            className="px-4 py-2 bg-green-100 text-green-700 rounded hover:bg-green-200 text-sm"
            disabled={loading}
          >
            💾 Verileri Kaydet
          </button>
          <button
            onClick={loadBudgetStatus}
            className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 text-sm"
            disabled={loading}
          >
            🔄 Durumu Yenile
          </button>
        </div>
      </div>
    </div>
  )
}

function ColorInput({ label, value, onChange }) {
  return (
    <label className="block text-sm space-y-1">
      <span className="text-gray-700">{label}</span>
      <div className="flex items-center gap-2">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="h-10 w-14 border rounded"
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="flex-1 border rounded px-3 py-2"
        />
      </div>
    </label>
  )
}
