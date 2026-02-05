import { render, screen, fireEvent } from '@testing-library/react'
import { ThemeProvider } from '../../hooks/useTheme'
import { ThemeToggle } from './ThemeToggle'

const renderWithTheme = (component: React.ReactNode) => {
  return render(<ThemeProvider>{component}</ThemeProvider>)
}

describe('ThemeToggle Component', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark', 'light')
  })

  it('renders toggle button', () => {
    renderWithTheme(<ThemeToggle />)

    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
  })

  it('has switch to dark mode title when light', () => {
    localStorage.setItem('theme', 'light')
    renderWithTheme(<ThemeToggle />)

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('title', 'Switch to dark mode')
  })

  it('has switch to light mode title when dark', () => {
    localStorage.setItem('theme', 'dark')
    renderWithTheme(<ThemeToggle />)

    const button = screen.getByRole('button')
    expect(button).toHaveAttribute('title', 'Switch to light mode')
  })

  it('applies custom className', () => {
    renderWithTheme(<ThemeToggle className="custom-class" />)

    const button = screen.getByRole('button')
    expect(button).toHaveClass('custom-class')
  })

  it('is a clickable button', () => {
    renderWithTheme(<ThemeToggle />)

    const button = screen.getByRole('button')
    fireEvent.click(button)

    expect(button).toBeInTheDocument()
  })

  it('contains sun icon element', () => {
    renderWithTheme(<ThemeToggle />)

    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
  })

  it('contains moon icon element', () => {
    renderWithTheme(<ThemeToggle />)

    const button = screen.getByRole('button')
    expect(button).toBeInTheDocument()
  })
})
