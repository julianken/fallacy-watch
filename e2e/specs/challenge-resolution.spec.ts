import { test, expect } from '@playwright/test'
import { AppPage } from '../pages/AppPage'
import singleConfirmed from '../fixtures/single-confirmed.json'
import cascadePair from '../fixtures/cascade-pair.json'

test.describe('challenge resolution', () => {
  test.describe('confirmed card', () => {
    let app!: AppPage

    test.beforeEach(async ({ page }) => {
      app = new AppPage(page)
      await app.mockAnalyze(singleConfirmed)
      await app.goto()
      await app.fillAndAnalyze('All experts agree that this is true.')
    })

    test('shows yes_label button', async () => {
      await expect(
        app.cardConfirmed('span_0').getByRole('button', { name: 'It is a fallacy' })
      ).toBeVisible()
    })

    test('confirm resolves card to resolved state', async () => {
      await app.cardConfirmed('span_0').getByRole('button', { name: 'It is a fallacy' }).click()
      await expect(app.cardConfirmed('span_0')).not.toBeVisible()
      await expect(app.cardResolved('span_0')).toBeVisible()
    })
  })

  test.describe('possibly card', () => {
    let app!: AppPage

    test.beforeEach(async ({ page }) => {
      app = new AppPage(page)
      await app.mockAnalyze(cascadePair)
      await app.goto()
      await app.fillAndAnalyze('Every scientist knows this proves our point.')
    })

    test('shows if_legitimate and if_fallacy panels', async () => {
      await expect(app.cardPossibly('span_1')).toContainText('The conclusion stands independently.')
    })

    test('clear resolves card to resolved state', async () => {
      await app.cardPossibly('span_1').getByRole('button', { name: 'It stands on its own' }).click()
      await expect(app.cardPossibly('span_1')).not.toBeVisible()
      await expect(app.cardResolved('span_1')).toBeVisible()
    })
  })
})
