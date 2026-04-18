import { test, expect } from '@playwright/test'
import { AppPage } from '../pages/AppPage'
import singleConfirmed from '../fixtures/single-confirmed.json'

test.describe('analyze flow', () => {
  test('analyze button enables after typing text', async ({ page }) => {
    const app = new AppPage(page)
    await app.goto()
    await app.textarea.fill('Some text to analyze')
    await expect(app.analyzeButton).toBeEnabled()
  })

  test.describe('after successful analysis', () => {
    let app!: AppPage

    test.beforeEach(async ({ page }) => {
      app = new AppPage(page)
      await app.mockAnalyze(singleConfirmed)
      await app.goto()
      await app.fillAndAnalyze('All experts agree that this is true.')
    })

    test('annotated text region is visible', async () => {
      await expect(app.annotatedText).toBeVisible()
    })

    test('meta line shows finding count and timing', async () => {
      await expect(app.metaLine).toContainText('1 finding · 42ms')
    })

    test('confirmed card is visible in findings list', async () => {
      await expect(app.cardConfirmed('span_0')).toBeVisible()
    })

    test('fallacy text is highlighted as a clickable button', async () => {
      await expect(app.highlight('All experts agree')).toBeVisible()
    })

    test('fallacy type is displayed in Title Case', async () => {
      await expect(app.cardConfirmed('span_0')).toContainText('Ad Populum')
    })
  })
})
