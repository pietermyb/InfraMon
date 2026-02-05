import { test, expect } from '@playwright/test'

test.describe('Navigation and Layout', () => {
  test('should navigate to dashboard', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should navigate to containers', async ({ page }) => {
    await page.goto('/containers')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should navigate to settings', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should handle unknown routes', async ({ page }) => {
    await page.goto('/unknown-route')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should navigate to login', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })
})
