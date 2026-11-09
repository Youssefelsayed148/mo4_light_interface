import { Monitor, Moon, Sun } from 'lucide-react'

import { cn } from '@/lib/utils'
import { useTheme, type ThemeMode } from '@/theme/theme-context'

const OPTIONS: { mode: ThemeMode; label: string; Icon: typeof Sun }[] = [
  { mode: 'system', label: 'System', Icon: Monitor },
  { mode: 'light', label: 'Light', Icon: Sun },
  { mode: 'dark', label: 'Dark', Icon: Moon },
]

export function ThemeSwitcher() {
  const { mode, setMode } = useTheme()
  return (
    <div
      role="group"
      aria-label="Theme"
      className="inline-flex rounded-lg border border-border bg-surface p-1"
    >
      {OPTIONS.map(({ mode: m, label, Icon }) => (
        <button
          key={m}
          type="button"
          aria-pressed={mode === m}
          onClick={() => setMode(m)}
          className={cn(
            'inline-flex h-9 items-center gap-2 rounded-md px-3 text-sm font-medium transition-colors duration-[var(--motion)]',
            mode === m ? 'bg-primary text-primary-foreground' : 'text-muted hover:text-text',
          )}
        >
          <Icon className="size-4" aria-hidden="true" />
          <span className="max-sm:sr-only">{label}</span>
        </button>
      ))}
    </div>
  )
}
