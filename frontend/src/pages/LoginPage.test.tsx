import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { ThemeProvider } from '../hooks/useTheme'
import { AuthProvider } from '../hooks/useAuth'
import LoginPage from './LoginPage'

const renderLogin = () => {
  return render(
    <MemoryRouter>
      <ThemeProvider>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </ThemeProvider>
    </MemoryRouter>
  )
}

describe('LoginPage', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('renders login form', () => {
    renderLogin()

    expect(screen.getByRole('heading', { name: /sign in/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument()
  })

  it('shows InfraMon branding in left panel', () => {
    renderLogin()

    const headings = screen.getAllByRole('heading', { name: /inframon/i })
    expect(headings.length).toBeGreaterThan(0)
  })

  it('renders username input field', () => {
    renderLogin()

    const usernameInput = screen.getByLabelText(/username/i)
    expect(usernameInput).toBeInTheDocument()
    expect(usernameInput).toHaveAttribute('type', 'text')
  })

  it('renders password input field', () => {
    renderLogin()

    const passwordInput = screen.getByLabelText(/password/i)
    expect(passwordInput).toBeInTheDocument()
    expect(passwordInput).toHaveAttribute('type', 'password')
  })

  it('has remember me checkbox', () => {
    renderLogin()

    expect(screen.getByText(/remember me/i)).toBeInTheDocument()
  })

  it('has forgot password link', () => {
    renderLogin()

    expect(screen.getByText(/forgot password/i)).toBeInTheDocument()
  })

  it('has demo credentials text', () => {
    renderLogin()

    expect(screen.getByText(/demo credentials/i)).toBeInTheDocument()
  })

  it('has terms and privacy links', () => {
    renderLogin()

    expect(screen.getByText(/terms of service/i)).toBeInTheDocument()
    expect(screen.getByText(/privacy policy/i)).toBeInTheDocument()
  })

  it('renders theme toggle button', () => {
    renderLogin()

    const themeToggle = screen.getByRole('button', { name: /switch to/i })
    expect(themeToggle).toBeInTheDocument()
  })

  it('accepts input in username field', () => {
    renderLogin()

    const usernameInput = screen.getByLabelText(/username/i)
    fireEvent.change(usernameInput, { target: { value: 'testuser' } })

    expect(usernameInput).toHaveValue('testuser')
  })

  it('accepts input in password field', () => {
    renderLogin()

    const passwordInput = screen.getByLabelText(/password/i)
    fireEvent.change(passwordInput, { target: { value: 'testpassword' } })

    expect(passwordInput).toHaveValue('testpassword')
  })

  it('shows welcome back heading', () => {
    renderLogin()

    expect(screen.getByRole('heading', { name: /welcome back/i })).toBeInTheDocument()
  })

  it('has welcome description text', () => {
    renderLogin()

    expect(screen.getByText(/monitor and manage your docker containers/i)).toBeInTheDocument()
  })
})
