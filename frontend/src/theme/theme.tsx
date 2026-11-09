import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

import { applyTheme, THEME_STORAGE_KEY, ThemeContext, type ThemeMode } from './theme-context'

function readStored(): ThemeMode {
  try {
    const v = localStorage.getItem(THEME_STORAGE_KEY)
    if (v === 'light' || v === 'dark' || v === 'system') return v
  } catch {
    /* storage unavailable: fall back to system */
  }
  return 'system'
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<ThemeMode>(readStored)

  useEffect(() => {
    applyTheme(mode)
  }, [mode])

  const setMode = useCallback((next: ThemeMode) => {
    setModeState(next)
    try {
      localStorage.setItem(THEME_STORAGE_KEY, next)
    } catch {
      /* ignore */
    }
  }, [])

  const value = useMemo(() => ({ mode, setMode }), [mode, setMode])
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
