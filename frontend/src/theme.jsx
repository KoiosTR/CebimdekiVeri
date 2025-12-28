import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

const ThemeContext = createContext()

const DEFAULT_THEME = {
  primary: '#4f46e5', // indigo-600
  primaryDark: '#4338ca',
  accent: '#22c55e', // green-500
  surface: '#ffffff',
  background: '#f5f5f7',
  text: '#0f172a',
}

function applyThemeVars(theme) {
  const root = document.documentElement
  root.style.setProperty('--color-primary', theme.primary)
  root.style.setProperty('--color-primary-dark', theme.primaryDark)
  root.style.setProperty('--color-accent', theme.accent)
  root.style.setProperty('--color-surface', theme.surface)
  root.style.setProperty('--color-background', theme.background)
  root.style.setProperty('--color-text', theme.text)
}

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => {
    try {
      const stored = localStorage.getItem('cv-theme')
      return stored ? JSON.parse(stored) : DEFAULT_THEME
    } catch {
      return DEFAULT_THEME
    }
  })

  useEffect(() => {
    applyThemeVars(theme)
    try {
      localStorage.setItem('cv-theme', JSON.stringify(theme))
    } catch {
      /* ignore */
    }
  }, [theme])

  const value = useMemo(() => ({ theme, setTheme, resetTheme: () => setTheme(DEFAULT_THEME) }), [theme])

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider')
  return ctx
}







