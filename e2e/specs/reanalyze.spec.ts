import { test, expect } from '@playwright/test'
import { AppPage } from '../pages/AppPage'
import singleConfirmed from '../fixtures/single-confirmed.json'
import emptyResult from '../fixtures/empty-result.json'

test.describe('re-analyze', () => {
  test('re-analyzing clears previous resolutions', async ({ page }) => {
    const app = new AppPage(page)

    // First analysis
    await app.mockAnalyze(singleConfirmed)
    await app.goto()
    await app.fillAndAnalyze('All experts agree that this is true.')
    await expect(app.cardConfirmed('span_0')).toBeVisible()

    // Resolve the card
    await app.cardConfirmed('span_0')
      .getByRole('button', { name: 'It is a fallacy' })
      .click()
    await expect(app.cardResolved('span_0')).toBeVisible()

    // Re-mock and re-analyze
    await app.mockAnalyze(singleConfirmed)
    await app.textarea.fill('Every expert knows this.')
    await app.analyzeButton.click()
    await expect(app.metaLine).toContainText('1 finding')

    // Previous resolved card must be gone; new card must be unresolved
    await expect(app.cardResolved('span_0')).not.toBeVisible()
    await expect(app.cardConfirmed('span_0')).toBeVisible()
  })

  test('re-analyzing with empty result clears previous findings', async ({ page }) => {
    const app = new AppPage(page)
    await app.mockAnalyze(singleConfirmed)
    await app.goto()
    await app.fillAndAnalyze('All experts agree.')
    await expect(app.cardConfirmed('span_0')).toBeVisible()

    await app.mockAnalyze(emptyResult)
    await app.textarea.fill('The sky is blue.')
    await app.analyzeButton.click()
    await expect(app.noFallaciesMessage).toBeVisible()
    await expect(app.cardConfirmed('span_0')).not.toBeVisible()
  })
})
