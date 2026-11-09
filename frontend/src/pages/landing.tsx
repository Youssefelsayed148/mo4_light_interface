import { Button } from '@/components/ui/button'
import { ThemeSwitcher } from '@/components/theme-switcher'

const SURFACES = [
  { name: 'bg', cls: 'bg-bg' },
  { name: 'surface', cls: 'bg-surface' },
  { name: 'border', cls: 'bg-border' },
  { name: 'text', cls: 'bg-text' },
  { name: 'muted', cls: 'bg-muted' },
]

const STATUSES = [
  { name: 'Unassigned', cls: 'text-status-unassigned' },
  { name: 'Assigned', cls: 'text-status-assigned' },
  { name: 'In progress', cls: 'text-status-in-progress' },
  { name: 'Ready / done', cls: 'text-status-done' },
  { name: 'Overdue / failed', cls: 'text-status-overdue' },
]

const ACCENTS = [
  { name: 'Indigo', cls: 'bg-accent-1' },
  { name: 'Teal', cls: 'bg-accent-2' },
  { name: 'Violet', cls: 'bg-accent-3' },
  { name: 'Amber', cls: 'bg-accent-4' },
]

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-lg border border-border bg-surface p-4 sm:p-6">
      <h2 className="mb-4 text-sm font-semibold text-muted">{title}</h2>
      {children}
    </section>
  )
}

export function Landing() {
  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col gap-4 px-4 py-6 sm:py-10">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">MO4 Light Interface</h1>
          <p className="text-muted">Phase 1 foundation. Theme tokens preview.</p>
        </div>
        <ThemeSwitcher />
      </header>

      <Section title="Surfaces and text">
        <ul className="grid grid-cols-2 gap-3 sm:grid-cols-5">
          {SURFACES.map((s) => (
            <li key={s.name} className="flex flex-col gap-2">
              <span className={`h-12 rounded-md border border-border ${s.cls}`} />
              <span className="text-sm">{s.name}</span>
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Status colors">
        <ul className="flex flex-wrap gap-2">
          {STATUSES.map((s) => (
            <li
              key={s.name}
              className={`rounded-full border border-border bg-bg px-3 py-1 text-sm font-medium ${s.cls}`}
            >
              {s.name}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Base accents (cycle)">
        <ul className="flex flex-wrap gap-4">
          {ACCENTS.map((a) => (
            <li key={a.name} className="flex items-center gap-2 text-sm">
              <span className={`size-4 rounded-full ${a.cls}`} aria-hidden="true" />
              {a.name}
            </li>
          ))}
        </ul>
      </Section>

      <Section title="Controls">
        <div className="flex flex-wrap gap-3">
          <Button>Primary</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
        </div>
      </Section>
    </main>
  )
}
