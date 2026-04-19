import { test, expect } from '@playwright/test'
import { AppPage } from '../pages/AppPage'
import cascadePair from '../fixtures/cascade-pair.json'

test.describe('highlight interaction', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 300 })
  })

  test('clicking span_1 highlight scrolls to its card', async ({ page }) => {
    const app = new AppPage(page)
    await app.mockAnalyze(cascadePair)
    await app.goto()
    await app.fillAndAnalyze('Every scientist knows this proves our point.')

    await app.highlight('this proves our point').click()

    await expect(app.cardPossibly('span_1')).toBeInViewport()
  })

  test('clicking span_0 highlight scrolls to its card', async ({ page }) => {
    const app = new AppPage(page)
    await app.mockAnalyze(cascadePair)
    await app.goto()
    await app.fillAndAnalyze('Every scientist knows this proves our point.')

    await app.highlight('Every scientist knows').click()

    await expect(app.cardConfirmed('span_0')).toBeInViewport()
  })
})
