import { test, expect } from '@playwright/test'
import { AppPage } from '../pages/AppPage'

test.describe('initial state', () => {
  test('shows fallacy-watch heading', async ({ page }) => {
    const app = new AppPage(page)
    await app.goto()
    await expect(page.getByRole('heading', { name: 'fallacy-watch' })).toBeVisible()
  })

  test('textarea is empty on load', async ({ page }) => {
    const app = new AppPage(page)
    await app.goto()
    await expect(app.textarea).toBeEmpty()
  })

  test('analyze button is disabled when textarea is empty', async ({ page }) => {
    const app = new AppPage(page)
    await app.goto()
    await expect(app.analyzeButton).toBeDisabled()
  })
})
