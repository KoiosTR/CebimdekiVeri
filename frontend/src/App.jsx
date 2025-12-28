import React, { useEffect, useMemo, useState } from 'react'
import { api } from './api'
import {
  PieChart, Pie, Cell, Tooltip as ReTooltip, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Legend,
  BarChart, Bar, AreaChart, Area
} from 'recharts'

import Chatbot from './components/Chatbot'

const COLORS = ['#60a5fa', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#14b8a6', '#f97316', '#22c55e']

export default function App() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [limitInfo, setLimitInfo] = useState(null)
  const [summary, setSummary] = useState({
    toplam_gelir: 0,
    toplam_gider: 0,
    tahmin: { gelir: 0, gider: 0 },
    gunluk_ozet: [],
    aylik_ozet: [],
    kategori_dagilimi: {},
  })
  const [aiOpen, setAiOpen] = useState(false)
  const [aiLoading, setAiLoading] = useState(false)
  const [aiMessage, setAiMessage] = useState('')

  const [form, setForm] = useState({
    islem_tipi: 'Gider',
    tutar: '',
    aciklama: '',
    user_email: '',
    kategori: '',
    kaynak: '',
    duzenliMi: false,
    zorunluMu: false,
    tarih: new Date().toISOString().slice(0, 10), // YYYY-MM-DD formatında bugünün tarihi
  })

  const kategoriData = useMemo(() => {
    const entries = Object.entries(summary.kategori_dagilimi || {})
    return entries.map(([name, value]) => ({ name, value }))
  }, [summary])

  // Günlük veriyi kullan (her zaman günlük veri göster)
  const chartData = useMemo(() => {
    const gunluk = summary.gunluk_ozet || []
    if (gunluk.length > 0) {
      // Günlük veriyi kullan
      return gunluk.map(item => ({
        tarih: item.gun,
        gelir: item.gelir || 0,
        gider: item.gider || 0
      }))
    }
    // Günlük veri yoksa aylık veriyi kullan
    const aylik = summary.aylik_ozet || []
    return aylik.map(item => ({
      tarih: item.ay,
      gelir: item.gelir || 0,
      gider: item.gider || 0
    }))
  }, [summary])

  // Kategori bar grafiği için veriyi azalan sırada hazırla
  const categoryBarData = useMemo(() => {
    const arr = [...(kategoriData || [])]
    arr.sort((a, b) => (b?.value || 0) - (a?.value || 0))
    return arr
  }, [kategoriData])

  // Kümülatif net bakiye (gelir - gider) alan grafiği verisi
  const cumulativeData = useMemo(() => {
    let running = 0
    return (chartData || []).map((d) => {
      running += (Number(d.gelir) || 0) - (Number(d.gider) || 0)
      return { tarih: d.tarih, bakiye: running }
    })
  }, [chartData])

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await api.get('/dashboard-data')
      setSummary(data)
    } catch (e) {
      setError(e?.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    try {
        const payload = {
          islem_tipi: form.islem_tipi,
          tutar: parseFloat(form.tutar),
          aciklama: form.aciklama || undefined,
          user_email: form.user_email || undefined,
          kategori: form.islem_tipi === 'Gider' ? (form.kategori || undefined) : undefined,
          kaynak: form.islem_tipi === 'Gelir' ? (form.kaynak || undefined) : undefined,
          duzenliMi: form.islem_tipi === 'Gelir' ? form.duzenliMi : undefined,
          zorunluMu: form.islem_tipi === 'Gider' ? form.zorunluMu : undefined,
          tarih: form.tarih || new Date().toISOString().slice(0, 10), // YYYY-MM-DD
        }
      const { data } = await api.post('/transactions', payload)
        if (data?.limit) {
          setLimitInfo(data.limit)
          if (data.limit.mesaj) {
            const variant = data.limit.asildi ? 'error' : 'warning'
            const title = data.limit.asildi ? 'Limit Aşıldı' : (data.limit.esik ? `%${data.limit.esik} Eşiği` : 'Limit Uyarısı')
            try { window.toast?.({ title, message: data.limit.mesaj, variant, duration: 0 }) } catch {}
          }
        }
        setForm({
          islem_tipi: 'Gider',
          tutar: '',
          aciklama: '',
          user_email: form.user_email || '',
          kategori: '',
          kaynak: '',
          duzenliMi: false,
          zorunluMu: false,
          tarih: new Date().toISOString().slice(0, 10) // Form gönderildikten sonra tarihi bugüne sıfırla
        })
      await load()
    } catch (e) {
      setError(e?.response?.data?.detail || e.message)
    }
  }

  return (
    <div className="min-h-screen max-w-6xl mx-auto space-y-6">
      {/* Hero / highlight */}
      <div className="card bg-gradient text-white p-6 flex items-center justify-between">
        <div>
          <div className="text-sm opacity-80">CebimdekiVeri</div>
          <h1 className="text-2xl font-semibold">Kişisel Finans Paneli</h1>
          <p className="text-sm opacity-80">Gelir-gider takibi, tahmin ve AI destekli öneriler.</p>
        </div>
        <div className="hidden md:block text-right text-sm opacity-90">
          <div>Tahmin (Gelir): <b>{summary?.tahmin?.gelir ?? 0}</b> TL</div>
          <div>Tahmin (Gider): <b>{summary?.tahmin?.gider ?? 0}</b> TL</div>
        </div>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Toplam Gelir" value={summary?.toplam_gelir ?? 0} color="text-green-600" />
        <StatCard label="Toplam Gider" value={summary?.toplam_gider ?? 0} color="text-red-600" />
        <StatCard label="Net Bakiye" value={(summary?.toplam_gelir ?? 0) - (summary?.toplam_gider ?? 0)} color="text-indigo-600" />
      </div>

      {/* Form + quick entry */}
      <section className="card p-5 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-lg">Hızlı Kayıt</h2>
            <p className="text-sm text-gray-500">Gelir/Gider ekleyin, grafikler güncellensin.</p>
          </div>
          {error && <p className="text-sm text-red-600">{String(error)}</p>}
        </div>
        <form className="grid grid-cols-1 md:grid-cols-6 gap-3 items-end" onSubmit={onSubmit}>
          <Field label="Tarih">
            <input
              type="date"
              className="w-full border rounded px-3 py-2"
              value={form.tarih}
              onChange={(e) => setForm((f) => ({ ...f, tarih: e.target.value }))}
              required
            />
          </Field>
          <Field label="Tutar">
            <input
              type="number"
              className="w-full border rounded px-3 py-2"
              placeholder="0"
              value={form.tutar}
              onChange={(e) => setForm((f) => ({ ...f, tutar: e.target.value }))}
              required
              min="0"
              step="0.01"
            />
          </Field>
          <Field label="Açıklama">
            <input
              type="text"
              className="w-full border rounded px-3 py-2"
              placeholder="Açıklama"
              value={form.aciklama}
              onChange={(e) => setForm((f) => ({ ...f, aciklama: e.target.value }))}
            />
          </Field>
          <Field label="Tip">
            <select
              className="w-full border rounded px-3 py-2"
              value={form.islem_tipi}
              onChange={(e) => setForm((f) => ({ ...f, islem_tipi: e.target.value }))}
            >
              <option value="Gider">Gider</option>
              <option value="Gelir">Gelir</option>
            </select>
          </Field>
          <Field label="Kullanıcı (e-posta)">
            <input
              type="text"
              className="w-full border rounded px-3 py-2"
              placeholder="ornek@eposta.com"
              value={form.user_email}
              onChange={(e) => setForm((f) => ({ ...f, user_email: e.target.value }))}
            />
          </Field>
          {form.islem_tipi === 'Gider' && (
            <>
              <Field label="Kategori">
                <input
                  type="text"
                  className="w-full border rounded px-3 py-2"
                  placeholder="Örn: Market"
                  value={form.kategori}
                  onChange={(e) => setForm((f) => ({ ...f, kategori: e.target.value }))}
                />
              </Field>
              <Field label="Zorunlu Gider">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4"
                    checked={form.zorunluMu}
                    onChange={(e) => setForm((f) => ({ ...f, zorunluMu: e.target.checked }))}
                  />
                  <span className="text-sm">Zorunlu gider</span>
                </label>
              </Field>
            </>
          )}
          {form.islem_tipi === 'Gelir' && (
            <>
              <Field label="Kaynak">
                <input
                  type="text"
                  className="w-full border rounded px-3 py-2"
                  placeholder="Örn: Şirket"
                  value={form.kaynak}
                  onChange={(e) => setForm((f) => ({ ...f, kaynak: e.target.value }))}
                />
              </Field>
              <Field label="Düzenli Gelir">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4"
                    checked={form.duzenliMi}
                    onChange={(e) => setForm((f) => ({ ...f, duzenliMi: e.target.checked }))}
                  />
                  <span className="text-sm">Düzenli gelir</span>
                </label>
              </Field>
            </>
          )}
          <div className="md:col-span-2">
            <button
              type="submit"
              className="btn-primary w-full"
              disabled={loading}
            >
              {loading ? 'Gönderiliyor...' : 'Kaydı Ekle'}
            </button>
          </div>
        </form>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card p-4">
          <h2 className="font-semibold mb-2">Harcama Dağılımı</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={kategoriData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={110}>
                  {kategoriData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <ReTooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card p-4">
          <h2 className="font-semibold mb-2">Gelir - Gider (Günlük/Aylık)</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="tarih"
                  tick={{ fontSize: 11 }}
                  angle={chartData.length > 7 ? -45 : 0}
                  textAnchor={chartData.length > 7 ? "end" : "middle"}
                  height={chartData.length > 7 ? 80 : 30}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Legend />
                <ReTooltip />
                <Line type="monotone" dataKey="gelir" stroke="#10b981" dot name="Gelir" strokeWidth={2} />
                <Line type="monotone" dataKey="gider" stroke="#ef4444" dot name="Gider" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="text-sm text-gray-600 mt-2 flex items-center gap-4">
            <span>Tahmin (Gelir): <b>{summary?.tahmin?.gelir ?? 0}</b> TL</span>
            <span>Tahmin (Gider): <b>{summary?.tahmin?.gider ?? 0}</b> TL</span>
          </div>
        </div>
        <div className="card p-4">
          <h2 className="font-semibold mb-2">Analiz Tablosu</h2>
          <div className="grid grid-cols-1 gap-4">
            <div>
              <div className="text-sm text-gray-600 mb-1">En Yüksek Kategoriler</div>
              <div className="max-h-40 overflow-auto border rounded">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-600 border-b">
                      <th className="py-1 px-2">Kategori</th>
                      <th className="py-1 px-2">Tutar</th>
                    </tr>
                  </thead>
                  <tbody>
                    {categoryBarData.slice(0, 8).map((row, idx) => (
                      <tr key={row.name + idx} className="border-b last:border-0">
                        <td className="py-1 px-2">{row.name}</td>
                        <td className="py-1 px-2 font-medium">{row.value}</td>
                      </tr>
                    ))}
                    {categoryBarData.length === 0 && (
                      <tr>
                        <td className="py-2 px-2 text-gray-500" colSpan={2}>Veri yok</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 mb-1">Son Günler</div>
              <div className="max-h-40 overflow-auto border rounded">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-600 border-b">
                      <th className="py-1 px-2">Tarih</th>
                      <th className="py-1 px-2">Gelir</th>
                      <th className="py-1 px-2">Gider</th>
                      <th className="py-1 px-2">Net</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chartData.slice(-10).map((d, i) => {
                      const net = (Number(d.gelir) || 0) - (Number(d.gider) || 0)
                      return (
                        <tr key={d.tarih + i} className="border-b last:border-0">
                          <td className="py-1 px-2">{d.tarih}</td>
                          <td className="py-1 px-2 text-green-700">{d.gelir}</td>
                          <td className="py-1 px-2 text-red-700">{d.gider}</td>
                          <td className={`py-1 px-2 font-medium ${net >= 0 ? 'text-green-700' : 'text-red-700'}`}>{net}</td>
                        </tr>
                      )
                    })}
                    {chartData.length === 0 && (
                      <tr>
                        <td className="py-2 px-2 text-gray-500" colSpan={4}>Veri yok</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="card p-4 lg:col-span-1">
          <h2 className="font-semibold mb-2">Kategori Bazlı Giderler</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryBarData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={categoryBarData.length > 6 ? -30 : 0} textAnchor={categoryBarData.length > 6 ? 'end' : 'middle'} height={categoryBarData.length > 6 ? 60 : 30} />
                <YAxis tick={{ fontSize: 12 }} />
                <Legend />
                <ReTooltip />
                <Bar dataKey="value" name="Tutar" fill="#60a5fa" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="card p-4 lg:col-span-2">
          <h2 className="font-semibold mb-2">Kümülatif Net Bakiye</h2>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={cumulativeData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="tarih" tick={{ fontSize: 11 }} angle={cumulativeData.length > 7 ? -45 : 0} textAnchor={cumulativeData.length > 7 ? 'end' : 'middle'} height={cumulativeData.length > 7 ? 80 : 30} />
                <YAxis tick={{ fontSize: 12 }} />
                <Legend />
                <ReTooltip />
                <Area type="monotone" dataKey="bakiye" name="Net Bakiye" stroke="#8b5cf6" fill="#c4b5fd" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="card p-4">
        <h2 className="font-semibold mb-2">Kategori Özeti</h2>
        <div className="overflow-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left text-gray-600 border-b">
                <th className="py-2 pr-4">Kategori</th>
                <th className="py-2">Tutar</th>
              </tr>
            </thead>
            <tbody>
              {categoryBarData.map((row, idx) => (
                <tr key={row.name + idx} className="border-b last:border-0">
                  <td className="py-2 pr-4">{row.name}</td>
                  <td className="py-2 font-medium">{row.value}</td>
                </tr>
              ))}
              {categoryBarData.length === 0 && (
                <tr>
                  <td className="py-3 text-gray-500" colSpan={2}>Gösterilecek kategori bulunamadı.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* AI / actions */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 card p-4">
          <Chatbot summary={summary} chartData={chartData} />
        </div>
        <div className="card p-4 space-y-3">
          <h3 className="font-semibold">Hızlı Eylemler</h3>
          <div className="space-y-2 text-sm text-gray-700">
            <p>• AI Chat için sol menüde “AI Chat” sayfasını açabilirsiniz.</p>
            <p>• Ayarlar’dan renk paletini değiştirip kendi temanızı oluşturun.</p>
            <p>• Grafiklerde tarihleri daraltmak için son günlerde kayıt ekleyin.</p>
          </div>
        </div>
      </section>
    </div>
  )
}

function StatCard({ label, value, color }) {
  return (
    <div className="card p-4">
      <div className="text-sm text-gray-500">{label}</div>
      <div className={`text-2xl font-semibold ${color}`}>{value}</div>
    </div>
  )
}

function Field({ label, children }) {
  return (
    <label className="text-sm space-y-1 block">
      <span className="text-gray-700">{label}</span>
      {children}
    </label>
  )
}
