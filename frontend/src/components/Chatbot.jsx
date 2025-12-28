import React, { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'

export default function Chatbot({ summary: summaryProp, chartData: chartDataProp, onAssistantMessage }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Merhaba! Finans özetini inceledim. Kısa soruların varsa sor, anında yorumlayayım. 💬' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState(summaryProp || null)
  const [chartData, setChartData] = useState(chartDataProp || [])
  const [image, setImage] = useState(null)
  const fileInputRef = useRef(null)
  const viewportRef = useRef(null)

  const scrollToBottom = () => {
    if (viewportRef.current) {
      viewportRef.current.scrollTop = viewportRef.current.scrollHeight
    }
  }

  useEffect(() => { scrollToBottom() }, [messages, loading])

  const computeChartData = (sum) => {
    if (!sum) return []
    const gunluk = sum.gunluk_ozet || []
    if (gunluk.length > 0) {
      return gunluk.map((item) => ({
        tarih: item.gun,
        gelir: item.gelir || 0,
        gider: item.gider || 0,
      }))
    }
    const aylik = sum.aylik_ozet || []
    return aylik.map((item) => ({
      tarih: item.ay,
      gelir: item.gelir || 0,
      gider: item.gider || 0,
    }))
  }

  useEffect(() => {
    if (summaryProp) {
      setSummary(summaryProp)
      setChartData(chartDataProp || computeChartData(summaryProp))
    }
  }, [summaryProp, chartDataProp])

  useEffect(() => {
    const load = async () => {
      if (summaryProp) return
      try {
        const { data } = await api.get('/dashboard-data')
        setSummary(data)
        setChartData(computeChartData(data))
      } catch (err) {
        // sessiz geç
      }
    }
    load()
  }, [summaryProp])

  const onFileChange = (e) => {
    const file = e.target.files?.[0]
    if (!file) {
      setImage(null)
      return
    }
    const reader = new FileReader()
    reader.onload = () => {
      const base64 = String(reader.result || '')
      const [, dataPart] = base64.split(',')
      setImage({ data: dataPart, mime_type: file.type, name: file.name })
    }
    reader.readAsDataURL(file)
  }

  const send = async (e) => {
    e?.preventDefault()
    const text = input.trim()
    if (!text || loading) return
    setMessages((m) => [...m, { role: 'user', content: text }])
    setInput('')
    setLoading(true)
    try {
      const payload = {
        message: text,
        chart_data: chartData,
        summary,
        image: image?.data ? { data: image.data, mime_type: image.mime_type } : undefined,
      }
      const { data } = await api.post('/ask-ai', payload)
      const reply = data?.message || 'Şu an yanıt veremiyorum.'
      setMessages((m) => [...m, { role: 'assistant', content: reply }])
      try { onAssistantMessage && onAssistantMessage(reply) } catch {}
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', content: String(err?.response?.data?.detail || err.message) }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b flex items-center justify-between bg-gradient text-white rounded-t-lg">
        <div className="font-semibold">🤖 AI Chatbot</div>
        <div className="text-xs opacity-90">Markdown + grafik/görsel analizi (Gemini)</div>
      </div>

      <div ref={viewportRef} className="flex-1 overflow-auto p-4 space-y-3 bg-white">
        {messages.map((m, i) => (
          <div key={i} className={`max-w-[85%] ${m.role === 'user' ? 'ml-auto text-right' : ''}`}>
            <div
              className={`inline-block px-3 py-2 rounded-2xl text-sm shadow-sm break-words ${
                m.role === 'user'
                  ? 'bg-[var(--color-primary)] text-white whitespace-pre-wrap'
                  : 'bg-gray-100 text-gray-900 text-left'
              }`}
            >
              {m.role === 'assistant' ? (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                </div>
              ) : (
                m.content
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-xs text-gray-500">Düşünüyorum… ⏳</div>
        )}
      </div>

      <form onSubmit={send} className="mt-3 flex items-center gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={onFileChange}
          className="hidden"
        />
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Sorunu yaz... Örn: Harcamalarımı nasıl azaltırım?"
          className="flex-1 border border-gray-300 rounded-full px-4 h-11 text-sm bg-white focus:outline-none focus:ring-0 focus:border-[var(--color-primary)]"
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="h-11 w-11 flex items-center justify-center rounded-full border border-gray-300 text-gray-600 hover:bg-gray-50"
          title="Görsel ekle"
        >
          📎
        </button>
        <button type="submit" disabled={loading} className="btn-primary text-sm h-11 px-5 rounded-full">
          Gönder
        </button>
      </form>
      {image?.name && (
        <div className="text-[11px] text-gray-500 mt-1 flex items-center gap-2">
          <span>Seçili: {image.name}</span>
          <button
            type="button"
            onClick={() => setImage(null)}
            className="text-[11px] px-2 py-1 border rounded text-gray-600 hover:bg-gray-50"
          >
            Kaldır
          </button>
        </div>
      )}
    </div>
  )
}
