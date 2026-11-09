import { createContext, useContext } from 'react'

export type ThemeMode = 'system' | 'light' | 'dark'
export const THEME_STORAGE_KEY = 'mo4-theme'

export interface ThemeContextValue {
  mode: ThemeMode
  setMode: (mode: ThemeMode) => void
}

export const ThemeContext = createContext<ThemeContextValue | null>(null)

/** "system" removes data-theme so the CSS media query decides. */
export function applyTheme(mode: ThemeMode) {
  const root = document.documentElement
  if (mode === 'system') root.removeAttribute('data-theme')
  else root.setAttribute('data-theme', mode)
}

export function useTheme() {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used inside ThemeProvider')
  return ctx
}
