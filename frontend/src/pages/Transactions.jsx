import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function Transactions() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedItem, setSelectedItem] = useState(null)
  const [showJson, setShowJson] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await api.get('/transactions')
      setItems(data?.items || [])
    } catch (e) {
      setError(e?.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const handleDelete = async (id) => {
    if (!confirm('Bu işlemi silmek istediğinize emin misiniz?')) {
      return
    }
    setLoading(true)
    setError(null)
    try {
      await api.delete(`/transactions/${id}`)
      await load() // Listeyi yenile
    } catch (e) {
      setError(e?.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  const hesaplaVergi = (tutar, duzenliMi) => {
    if (!tutar || tutar <= 0) return 0
    let vergi_orani = 0.15
    if (tutar > 230000) {
      vergi_orani = 0.27
    } else if (tutar > 110000) {
      vergi_orani = 0.20
    }
    let vergi = tutar * vergi_orani
    if (duzenliMi) {
      vergi *= 0.95
    }
    return Math.round(vergi * 100) / 100
  }

  const taksitVarMi = (tutar, kategori) => {
    if (!tutar || tutar < 1000) return false
    const kategoriUpper = (kategori || "").toUpperCase()
    const taksitKategorileri = ["FATURA", "KREDI", "TAKSIT", "KREDİ", "ÖDEME"]
    return taksitKategorileri.some(k => kategoriUpper.includes(k))
  }

  const getDetay = (it) => {
    const tip = it.Islem_Tipi || '-'
    let detay = `${tip} - ${it.Aciklama || '-'}\n`
    detay += `Tutar: ${it.Tutar ?? '-'} TL\n`
    detay += `Tarih: ${it.Tarih ? String(it.Tarih).slice(0, 10) : '-'}\n`
    if (it.User_Email) {
      detay += `Kullanıcı: ${it.User_Email}\n`
    }
    if (it.Kaynak) {
      detay += `Kaynak: ${it.Kaynak}\n`
    }
    if (it.DuzenliMi !== undefined) {
      detay += `Düzenli Gelir: ${it.DuzenliMi ? 'Evet' : 'Hayır'}\n`
      detay += `Tahmini Vergi: ${hesaplaVergi(it.Tutar, it.DuzenliMi)} TL\n`
    }
    if (it.Kategori) {
      detay += `Kategori: ${it.Kategori}\n`
    }
    if (it.ZorunluMu !== undefined) {
      detay += `Zorunlu Gider: ${it.ZorunluMu ? 'Evet' : 'Hayır'}\n`
      detay += `Taksitli: ${taksitVarMi(it.Tutar, it.Kategori) ? 'Evet' : 'Hayır'}\n`
    }
    if (it.id) {
      detay += `ID: ${it.id}`
    }
    return detay.trim()
  }

  const toJSON = (it) => {
    const json = {
      id: it.id,
      tutar: it.Tutar,
      aciklama: it.Aciklama,
      tarih: it.Tarih,
      user_email: it.User_Email,
      islem_tipi: it.Islem_Tipi,
      kaynak: it.Kaynak,
      kategori: it.Kategori,
    }
    if (it.DuzenliMi !== undefined) {
      json.duzenliMi = it.DuzenliMi
      json.tahmini_vergi = hesaplaVergi(it.Tutar, it.DuzenliMi)
    }
    if (it.ZorunluMu !== undefined) {
      json.zorunluMu = it.ZorunluMu
      json.taksitVarMi = taksitVarMi(it.Tutar, it.Kategori)
    }
    return JSON.stringify(json, null, 2)
  }

  const handleShowDetay = (it) => {
    if (selectedItem?.id === it.id && !showJson) {
      setSelectedItem(null)
    } else {
      setSelectedItem(it)
      setShowJson(false)
    }
  }

  const handleShowJson = (it) => {
    if (selectedItem?.id === it.id && showJson) {
      setSelectedItem(null)
    } else {
      setSelectedItem(it)
      setShowJson(true)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-semibold">İşlemler</h1>
        <button onClick={load} className="px-3 py-2 rounded bg-gray-800 text-white text-sm" disabled={loading}>
          {loading ? 'Yükleniyor...' : 'Yenile'}
        </button>
      </div>
      {error && <p className="text-sm text-red-600 mb-2">{String(error)}</p>}
      <div className="overflow-auto bg-white rounded shadow">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b bg-gray-50 text-gray-600">
              <th className="text-left px-3 py-2">Tarih</th>
              <th className="text-left px-3 py-2">Tip</th>
              <th className="text-left px-3 py-2">Kategori/Kaynak</th>
              <th className="text-left px-3 py-2">Açıklama</th>
              <th className="text-left px-3 py-2">Kullanıcı</th>
              <th className="text-right px-3 py-2">Tutar</th>
              <th className="text-center px-3 py-2">Özellikler</th>
              <th className="text-center px-3 py-2">İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it) => (
              <React.Fragment key={it.id}>
                <tr className="border-b last:border-b-0 hover:bg-gray-50">
                  <td className="px-3 py-2">{it.Tarih ? String(it.Tarih).slice(0, 10) : '-'}</td>
                  <td className="px-3 py-2">
                    <span className={`px-2 py-1 rounded text-xs ${it.Islem_Tipi === 'Gelir' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {it.Islem_Tipi || '-'}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    {it.Islem_Tipi === 'Gelir' ? (it.Kaynak || '-') : (it.Kategori || '-')}
                  </td>
                  <td className="px-3 py-2">{it.Aciklama || '-'}</td>
                  <td className="px-3 py-2 text-xs">{it.User_Email || '-'}</td>
                  <td className="px-3 py-2 text-right font-semibold">{it.Tutar ?? '-'} TL</td>
                  <td className="px-3 py-2 text-center">
                    {it.Islem_Tipi === 'Gelir' && it.DuzenliMi !== undefined && (
                      <div className="flex flex-col gap-1 items-center">
                        {it.DuzenliMi && (
                          <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded" title="Düzenli Gelir">
                            🔄 Düzenli
                          </span>
                        )}
                        {it.DuzenliMi !== undefined && it.Tutar > 0 && (
                          <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded" title="Tahmini Vergi">
                            💰 {hesaplaVergi(it.Tutar, it.DuzenliMi)} TL
                          </span>
                        )}
                      </div>
                    )}
                    {it.Islem_Tipi === 'Gider' && it.ZorunluMu !== undefined && (
                      <div className="flex flex-col gap-1 items-center">
                        {it.ZorunluMu && (
                          <span className="px-2 py-0.5 text-xs bg-orange-100 text-orange-700 rounded" title="Zorunlu Gider">
                            ⚠️ Zorunlu
                          </span>
                        )}
                        {taksitVarMi(it.Tutar, it.Kategori) && (
                          <span className="px-2 py-0.5 text-xs bg-yellow-100 text-yellow-700 rounded" title="Taksitli">
                            📅 Taksitli
                          </span>
                        )}
                        {!it.ZorunluMu && !taksitVarMi(it.Tutar, it.Kategori) && (
                          <span className="text-xs text-gray-400">-</span>
                        )}
                      </div>
                    )}
                    {it.Islem_Tipi === 'Gider' && it.ZorunluMu === undefined && (
                      <span className="text-xs text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-center">
                    <div className="flex gap-1 justify-center">
                      <button
                        onClick={() => handleShowDetay(it)}
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                        title="Detayları Göster"
                      >
                        📋
                      </button>
                      <button
                        onClick={() => handleShowJson(it)}
                        className="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
                        title="JSON Göster"
                      >
                        📄 JSON
                      </button>
                      <button
                        onClick={() => handleDelete(it.id)}
                        className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                        title="Sil"
                        disabled={loading}
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
                {selectedItem?.id === it.id && (
                  <tr>
                    <td colSpan={8} className="px-4 py-3 bg-gray-50 border-b">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold text-sm">İşlem Detayları</h3>
                          <button
                            onClick={() => setSelectedItem(null)}
                            className="text-xs text-gray-500 hover:text-gray-700"
                          >
                            ✕ Kapat
                          </button>
                        </div>
                        {showJson ? (
                          <pre className="text-xs bg-white p-3 rounded border overflow-auto max-h-48">
                            {toJSON(it)}
                          </pre>
                        ) : (
                          <pre className="text-xs whitespace-pre-wrap bg-white p-3 rounded border">
                            {getDetay(it)}
                          </pre>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
            {items.length === 0 && (
              <tr>
                <td className="px-3 py-6 text-center text-gray-500" colSpan={8}>Kayıt bulunamadı.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
