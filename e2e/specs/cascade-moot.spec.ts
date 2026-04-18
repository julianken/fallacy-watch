import { test, expect } from '@playwright/test'
import { AppPage } from '../pages/AppPage'
import cascadePair from '../fixtures/cascade-pair.json'

test.describe('cascade → moot', () => {
  let app!: AppPage

  test.beforeEach(async ({ page }) => {
    app = new AppPage(page)
    await app.mockAnalyze(cascadePair)
    await app.goto()
    await app.fillAndAnalyze('Every scientist knows this proves our point.')
  })

  test('possibly card is visible before any interaction', async () => {
    await expect(app.cardPossibly('span_1')).toBeVisible()
  })

  test('confirming source span makes dependent span moot', async () => {
    await app.cardConfirmed('span_0').getByRole('button', { name: 'Fallacy confirmed' }).click()
    await expect(app.cardPossibly('span_1')).not.toBeVisible()
    await expect(app.cardMoot('span_1')).toBeVisible()
  })

  test('moot card shows cascade reason', async () => {
    await app.cardConfirmed('span_0').getByRole('button', { name: 'Fallacy confirmed' }).click()
    await expect(app.cardMoot('span_1')).toContainText('Premise failure makes this conclusion moot.')
  })

  test('"review anyway" restores possibly card', async () => {
    await app.cardConfirmed('span_0').getByRole('button', { name: 'Fallacy confirmed' }).click()
    await app.cardMoot('span_1').getByRole('button', { name: 'Review anyway →' }).click()
    await expect(app.cardMoot('span_1')).not.toBeVisible()
    await expect(app.cardPossibly('span_1')).toBeVisible()
  })
})
