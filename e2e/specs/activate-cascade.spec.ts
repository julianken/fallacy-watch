import { test, expect } from '@playwright/test'
import { AppPage } from '../pages/AppPage'
import activatePair from '../fixtures/activate-pair.json'

test.describe('activate cascade', () => {
  test('activate cascade does not overwrite a previously resolved span', async ({ page }) => {
    const app = new AppPage(page)
    await app.mockAnalyze(activatePair)
    await app.goto()
    await app.fillAndAnalyze('First claim. Second claim.')

    // Resolve span_1 first (the activate target)
    await app.cardPossibly('span_1').getByRole('button', { name: 'Not circular' }).click()
    await expect(app.cardResolved('span_1')).toBeVisible()

    // Now resolve span_0 — this fires the activate rule targeting span_1
    await app.cardConfirmed('span_0').getByRole('button', { name: 'Yes fallacy' }).click()

    // span_1 must STILL be resolved — activate must not overwrite it
    await expect(app.cardResolved('span_1')).toBeVisible()
    await expect(app.cardPossibly('span_1')).not.toBeVisible()
  })
})
