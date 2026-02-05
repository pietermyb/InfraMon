import { test as base, Page, Locator, expect } from '@playwright/test'

export { expect }

export const test = base.extend({
  page: async ({ page }, use) => {
    page.on('console', msg => {
      if (msg.type() === 'error') {
        console.error('Console error:', msg.text())
      }
    })

    page.on('pageerror', err => {
      console.error('Page error:', err.message)
    })

    await use(page)
  },
})

export async function waitForUrl(page: Page, urlPattern: RegExp | string, timeout = 5000) {
  await page.waitForURL(urlPattern, { timeout })
}

export async function waitForLoad(page: Page) {
  await page.waitForLoadState('networkidle')
  await page.waitForLoadState('domcontentloaded')
}

export function getByRoleButton(name: string): (page: Page) => Locator {
  return (page: Page) => page.getByRole('button', { name })
}

export function getByRoleLink(name: string): (page: Page) => Locator {
  return (page: Page) => page.getByRole('link', { name })
}

export function getByRoleHeading(text: string): (page: Page) => Locator {
  return (page: Page) => page.getByRole('heading', { text })
}

export async function loginAsAdmin(page: Page) {
  await page.evaluate(() => {
    localStorage.setItem('token', 'fake-token')
    localStorage.setItem('refresh_token', 'fake-refresh-token')
    localStorage.setItem('user', JSON.stringify({ id: 1, username: 'admin', email: 'admin@example.com' }))
  })
}

export async function logout(page: Page) {
  await page.evaluate(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  })
}

export async function mockApiResponse(page: Page, path: string, response: object) {
  await page.route(path, async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(response)
    })
  })
}

export async function mockApiError(page: Page, path: string, error: object, status = 400) {
  await page.route(path, async route => {
    await route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(error)
    })
  })
}
