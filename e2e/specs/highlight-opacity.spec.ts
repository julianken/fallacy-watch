import { test, expect } from '@playwright/test'
import { AppPage } from '../pages/AppPage'
import singleConfirmed from '../fixtures/single-confirmed.json'

test.describe('highlight opacity', () => {
  test('CLEARED resolution dims the corresponding inline highlight', async ({ page }) => {
    const app = new AppPage(page)
    await app.mockAnalyze(singleConfirmed)
    await app.goto()
    await app.fillAndAnalyze('All experts agree that this is true.')

    // Resolve as CLEARED (NO button)
    await app.cardConfirmed('span_0')
      .getByRole('button', { name: 'It is not a fallacy' })
      .click()
    await expect(app.cardResolved('span_0')).toBeVisible()

    // The mark must be dimmed
    const dimmedCount = await page.evaluate(() =>
      [...document.querySelectorAll('mark')].filter(
        m => (m as HTMLElement).style.opacity === '0.4'
      ).length
    )
    expect(dimmedCount).toBe(1)
  })

  test('CONFIRMED resolution keeps the inline highlight at full opacity', async ({ page }) => {
    const app = new AppPage(page)
    await app.mockAnalyze(singleConfirmed)
    await app.goto()
    await app.fillAndAnalyze('All experts agree that this is true.')

    // Resolve as CONFIRMED (YES button)
    await app.cardConfirmed('span_0')
      .getByRole('button', { name: 'It is a fallacy' })
      .click()
    await expect(app.cardResolved('span_0')).toBeVisible()

    // Verify marks exist before checking opacity — guards against vacuous pass if annotated text never rendered
    const markCount = await page.evaluate(() => document.querySelectorAll('mark').length)
    expect(markCount).toBeGreaterThan(0)

    const dimmedCount = await page.evaluate(() =>
      [...document.querySelectorAll('mark')].filter(
        m => (m as HTMLElement).style.opacity === '0.4'
      ).length
    )
    expect(dimmedCount).toBe(0)
  })
})
