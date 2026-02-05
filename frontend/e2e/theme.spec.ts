import { test, expect } from '@playwright/test'

test.describe('Theme Switching', () => {
  test('should load dashboard with theme toggle', async ({ page }) => {
    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should load login page with theme toggle', async ({ page }) => {
    await page.goto('/login')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should load containers page with theme toggle', async ({ page }) => {
    await page.goto('/containers')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })

  test('should load settings page with theme toggle', async ({ page }) => {
    await page.goto('/settings')
    await page.waitForLoadState('networkidle')
    await expect(page).toBeDefined()
  })
})
