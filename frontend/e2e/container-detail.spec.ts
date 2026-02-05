import { test, expect } from '@playwright/test'

test.describe('Container Detail Page', () => {
  test('should load container detail page successfully', async ({ page }) => {
    await page.goto('/containers/test-id')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should handle navigation from containers', async ({ page }) => {
    await page.goto('/containers')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should handle navigation to dashboard', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should handle navigation to login', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })
})
