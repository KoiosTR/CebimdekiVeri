import React, { useEffect, useMemo, useState } from 'react'
import Chatbot from '../components/Chatbot'
import { api } from '../api'
import {
  PieChart, Pie, Cell, Tooltip as ReTooltip, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Legend
} from 'recharts'

export default function Chat() {
  const [summary, setSummary] = useState({
    toplam_gelir: 0,
    toplam_gider: 0,
    tahmin: { gelir: 0, gider: 0 },
    gunluk_ozet: [],
    aylik_ozet: [],
    kategori_dagilimi: {},
  })
  const [chartData, setChartData] = useState([])

  useEffect(() => {
    const load = async () => {
      try {
        const { data } = await api.get('/dashboard-data')
        setSummary(data)
        const gunluk = data.gunluk_ozet || []
        if (gunluk.length > 0) {
          setChartData(gunluk.map((item) => ({ tarih: item.gun, gelir: item.gelir || 0, gider: item.gider || 0 })))
        } else {
          const aylik = data.aylik_ozet || []
          setChartData(aylik.map((item) => ({ tarih: item.ay, gelir: item.gelir || 0, gider: item.gider || 0 })))
        }
      } catch {}
    }
    load()
  }, [])

  const kategoriData = useMemo(() => {
    const entries = Object.entries(summary.kategori_dagilimi || {})
    return entries.map(([name, value]) => ({ name, value }))
  }, [summary])

  const categoryBarData = useMemo(() => {
    const arr = [...(kategoriData || [])]
    arr.sort((a, b) => (b?.value || 0) - (a?.value || 0))
    return arr
  }, [kategoriData])

  const COLORS = ['#60a5fa', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6', '#14b8a6', '#f97316', '#22c55e']

  

  return (
    <div className="space-y-4">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">AI Chatbot</h1>
        <p className="text-sm text-gray-600">Kısa, net yanıtlar. Finans sorularını sor, anında yanıt al.</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 card p-0 overflow-hidden">
          <Chatbot />
        </div>
        <div className="space-y-4">
          <div className="card p-4">
            <h3 className="font-semibold mb-2">Harcama Dağılımı</h3>
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={kategoriData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90}>
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
            <h3 className="font-semibold mb-2">Gelir - Gider</h3>
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="tarih" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Legend />
                  <ReTooltip />
                  <Line type="monotone" dataKey="gelir" stroke="#10b981" dot={false} name="Gelir" strokeWidth={2} />
                  <Line type="monotone" dataKey="gider" stroke="#ef4444" dot={false} name="Gider" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card p-4">
            <h3 className="font-semibold mb-2">Analiz Tablosu</h3>
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
        </div>
      </div>
    </div>
  )
}







