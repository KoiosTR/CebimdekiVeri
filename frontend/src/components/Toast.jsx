import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react'

const ToastContext = createContext({ add: () => {} })

function ToastItem({ id, title, message, variant = 'info', onClose, duration }) {
  const timerRef = useRef(null)
  useEffect(() => {
    if (duration && duration > 0) {
      timerRef.current = setTimeout(() => onClose(id), duration)
      return () => clearTimeout(timerRef.current)
    }
    return () => {}
  }, [id, onClose, duration])

  const style = useMemo(() => {
    switch (variant) {
      case 'error':
        return 'bg-red-600 text-white border-red-700'
      case 'warning':
        return 'bg-yellow-500 text-black border-yellow-600'
      case 'success':
        return 'bg-emerald-600 text-white border-emerald-700'
      default:
        return 'bg-indigo-600 text-white border-indigo-700'
    }
  }, [variant])

  return (
    <div className={`pointer-events-auto w-80 shadow-lg rounded-lg border ${style} animate-slide-in`}
         role="alert">
      <div className="p-3">
        {title && <div className="text-sm font-semibold">{title}</div>}
        {message && <div className="text-sm opacity-95 leading-snug mt-0.5 whitespace-pre-wrap">{message}</div>}
      </div>
      <button onClick={() => onClose(id)}
              className="absolute top-2 right-2 text-xs opacity-75 hover:opacity-100">
        ✕
      </button>
    </div>
  )
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const remove = (id) => setToasts((list) => list.filter((t) => t.id !== id))

  const add = ({ title, message, variant = 'info', duration }) => {
    const id = Math.random().toString(36).slice(2)
    setToasts((list) => [{ id, title, message, variant, duration }, ...list].slice(0, 5))
    return id
  }

  useEffect(() => {
    // Global yardımcı: window.toast({ message, variant, title })
    window.toast = (msg, opts = {}) => {
      if (typeof msg === 'string') {
        return add({ message: msg, ...opts })
      }
      // objeyse: { message, title, variant }
      return add(msg || {})
    }
    return () => { try { delete window.toast } catch {} }
  }, [])

  return (
    <ToastContext.Provider value={{ add, remove }}>
      {children}
      <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 items-end pointer-events-none">
        {toasts.map((t) => (
          <ToastItem key={t.id} {...t} onClose={remove} />
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  return useContext(ToastContext)
}

// Minimal enter animasyonu için tailwind'e ek sınıf yoksa basit keyframes
// Tailwind kullanılmıyorsa, global CSS'de .animate-slide-in tanımlı olmalı.
