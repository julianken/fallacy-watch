import { test, expect, type Route } from '@playwright/test'
import { AppPage } from '../pages/AppPage'
import emptyResult from '../fixtures/empty-result.json'

test.describe('error and edge cases', () => {
  test('network error shows error message', async ({ page }) => {
    const app = new AppPage(page)
    await app.abortAnalyze()
    await app.goto()
    await app.fillAndAnalyze('trigger a network error')
    await expect(app.errorMessage).toBeVisible()
    await expect(app.errorMessage).toContainText('Analysis failed')
  })

  test('analyze button re-enables after network error', async ({ page }) => {
    const app = new AppPage(page)
    await app.abortAnalyze()
    await app.goto()
    await app.fillAndAnalyze('trigger a network error')
    await expect(app.analyzeButton).toBeEnabled()
  })

  test('empty result shows no-fallacies message', async ({ page }) => {
    const app = new AppPage(page)
    await app.mockAnalyze(emptyResult)
    await app.goto()
    await app.fillAndAnalyze('text with no fallacies detected')
    await expect(app.noFallaciesMessage).toBeVisible()
    await expect(app.noFallaciesMessage).toContainText('No argument fallacies detected')
  })

  test('analyze button is disabled during loading', async ({ page }) => {
    const app = new AppPage(page)
    let unblock!: () => void
    const blocker = new Promise<void>(resolve => { unblock = resolve })
    await page.route('**/analyze', async (route: Route) => {
      await blocker
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(emptyResult),
      })
    })
    await app.goto()
    await app.textarea.fill('test text')
    await app.analyzeButton.click()
    await expect(app.analyzeButton).toBeDisabled()
    unblock()
  })
})
