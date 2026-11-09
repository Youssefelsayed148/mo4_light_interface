import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import App from './App'
import { THEME_STORAGE_KEY } from './theme/theme-context'

const root = () => document.documentElement

describe('landing + theme switcher', () => {
  it('renders the token preview', () => {
    render(<App />)
    expect(screen.getByRole('heading', { name: 'MO4 Light Interface' })).toBeInTheDocument()
    expect(screen.getByText('Overdue / failed')).toBeInTheDocument()
    expect(screen.getByText('Violet')).toBeInTheDocument()
  })

  it('defaults to system (no data-theme attribute)', () => {
    render(<App />)
    expect(root()).not.toHaveAttribute('data-theme')
    expect(screen.getByRole('button', { name: 'System' })).toHaveAttribute('aria-pressed', 'true')
  })

  it('switches to light and dark, persists, and returns to system', async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByRole('button', { name: 'Light' }))
    expect(root()).toHaveAttribute('data-theme', 'light')
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('light')

    await user.click(screen.getByRole('button', { name: 'Dark' }))
    expect(root()).toHaveAttribute('data-theme', 'dark')

    await user.click(screen.getByRole('button', { name: 'System' }))
    expect(root()).not.toHaveAttribute('data-theme')
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('system')
  })

  it('restores the saved mode and is keyboard operable', async () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'dark')
    const user = userEvent.setup()
    render(<App />)
    expect(root()).toHaveAttribute('data-theme', 'dark')

    screen.getByRole('button', { name: 'Light' }).focus()
    await user.keyboard('{Enter}')
    expect(root()).toHaveAttribute('data-theme', 'light')
  })
})
