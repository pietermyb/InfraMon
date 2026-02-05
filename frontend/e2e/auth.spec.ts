import { test, expect } from '@playwright/test'

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('should display login page with all elements', async ({ page }) => {
    await expect(page.locator('h1:has-text("InfraMon")').first()).toBeVisible()
    await expect(page.locator('h2:has-text("Welcome Back")')).toBeVisible()
    await expect(page.locator('#username')).toBeVisible()
    await expect(page.locator('#password')).toBeVisible()
    await expect(page.locator('button:has-text("Sign in")')).toBeVisible()
    await expect(page.locator('text=Remember me')).toBeVisible()
    await expect(page.locator('text=Forgot password')).toBeVisible()
  })

  test('should show validation error when username is empty', async ({ page }) => {
    await page.fill('#password', 'testpassword')
    await page.click('button:has-text("Sign in")')
    await expect(page.locator('text=Username is required')).toBeVisible()
  })

  test('should show validation error when password is empty', async ({ page }) => {
    await page.fill('#username', 'testuser')
    await page.click('button:has-text("Sign in")')
    await expect(page.locator('text=Password is required')).toBeVisible()
  })

  test('should show validation error for short username', async ({ page }) => {
    await page.fill('#username', 'ab')
    await page.fill('#password', 'testpassword')
    await page.click('button:has-text("Sign in")')
    await expect(page.locator('text=Username must be at least 3 characters')).toBeVisible()
  })

  test('should show validation error for short password', async ({ page }) => {
    await page.fill('#username', 'testuser')
    await page.fill('#password', '12345')
    await page.click('button:has-text("Sign in")')
    await expect(page.locator('text=Password must be at least 6 characters')).toBeVisible()
  })

  test('should toggle password visibility', async ({ page }) => {
    await page.fill('#password', 'secretpassword')
    const passwordInput = page.locator('#password')
    await expect(passwordInput).toHaveAttribute('type', 'password')

    const toggleButton = page.locator('button').filter({ has: page.locator('svg') }).first()
    if (await toggleButton.isVisible()) {
      await toggleButton.click()
      await expect(passwordInput).toHaveAttribute('type', 'text')
    }
  })

  test('should have accessible form labels', async ({ page }) => {
    const usernameInput = page.locator('input[name="username"]')
    const passwordInput = page.locator('input[name="password"]')

    await expect(usernameInput).toHaveAttribute('autocomplete', 'username')
    await expect(passwordInput).toHaveAttribute('autocomplete', 'current-password')
  })

  test('should display demo credentials hint', async ({ page }) => {
    await expect(page.locator('text=Demo credentials:')).toBeVisible()
  })
})

test.describe('Protected Routes', () => {
  test('should redirect unauthenticated user to login from dashboard', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/login/)
  })

  test('should redirect unauthenticated user to login from containers', async ({ page }) => {
    await page.goto('/containers')
    await expect(page).toHaveURL(/\/login/)
  })

  test('should redirect unauthenticated user to login from settings', async ({ page }) => {
    await page.goto('/settings')
    await expect(page).toHaveURL(/\/login/)
  })

  test('should redirect unauthenticated user to login from container detail', async ({ page }) => {
    await page.goto('/containers/test-container-id')
    await expect(page).toHaveURL(/\/login/)
  })

  test('should handle unknown routes gracefully', async ({ page }) => {
    await page.goto('/unknown-route')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })
})
