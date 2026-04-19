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

    test('shows both if_legitimate and if_fallacy columns with text', async () => {
      const card = app.cardPossibly('span_1')

      await expect(card.getByText('IF LEGITIMATE', { exact: false })).toBeVisible()
      await expect(card.getByText('IF A FALLACY', { exact: false })).toBeVisible()

      await expect(card.getByText('The conclusion stands independently.')).toBeVisible()
      await expect(card.getByText('The argument is circular.')).toBeVisible()
    })
  })

  test('does not show legitimacy comparison when fields are null', async ({ page }) => {
    const app = new AppPage(page)
    const possiblyNoComparison = {
      spans: [{
        id: 'span_0',
        text: 'All experts agree',
        start: 0, end: 17,
        status: 'possibly',
        fallacy_type: 'Ad Populum',
        explanation: 'Appeals to consensus.',
        challenge: {
          type: 'premise_check',
          question: { text: 'Is this a fallacy?', yes_label: 'Yes', no_label: 'No' }
        },
        if_legitimate: null,
        if_fallacy: null,
        content_generated: true,
      }],
      rules: [],
      meta: { sentence_count: 1, argument_span_count: 1, fallacy_count: 1, processing_ms: 10 },
    }
    await app.mockAnalyze(possiblyNoComparison)
    await app.goto()
    await app.fillAndAnalyze('All experts agree.')

    await expect(app.cardPossibly('span_0')).toBeVisible()
    await expect(
      app.cardPossibly('span_0').getByText('IF LEGITIMATE', { exact: false })
    ).not.toBeVisible()
    await expect(
      app.cardPossibly('span_0').getByText('IF A FALLACY', { exact: false })
    ).not.toBeVisible()
  })
})
