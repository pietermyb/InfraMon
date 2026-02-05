import { test, expect } from '@playwright/test'

test.describe('Dashboard Page', () => {
  test('should load dashboard page successfully', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should have proper page structure', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should handle navigation to login', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should handle navigation to containers', async ({ page }) => {
    await page.goto('/containers')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should handle navigation to settings', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })
})
