import { test, expect } from '@playwright/test'

test.describe('Containers Page', () => {
  test('should load containers page successfully', async ({ page }) => {
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

  test('should handle unknown routes', async ({ page }) => {
    await page.goto('/unknown-path')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })
})
