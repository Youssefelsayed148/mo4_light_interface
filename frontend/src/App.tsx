import { Landing } from '@/pages/landing'
import { ThemeProvider } from '@/theme/theme'

export default function App() {
  return (
    <ThemeProvider>
      <Landing />
    </ThemeProvider>
  )
}
