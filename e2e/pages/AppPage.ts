import type { Page, Locator, Route } from '@playwright/test'

export class AppPage {
  readonly page: Page
  readonly textarea: Locator
  readonly analyzeButton: Locator
  readonly annotatedText: Locator
  readonly findingsList: Locator
  readonly metaLine: Locator
  readonly errorMessage: Locator
  readonly noFallaciesMessage: Locator

  constructor(page: Page) {
    this.page = page
    this.textarea = page.getByLabel('Text to analyze for argument fallacies')
    this.analyzeButton = page.getByTestId('analyze-button')
    this.annotatedText = page.getByTestId('annotated-text')
    this.findingsList = page.getByTestId('findings-list')
    this.metaLine = page.getByTestId('meta-line')
    this.errorMessage = page.getByTestId('error-message')
    this.noFallaciesMessage = page.getByTestId('no-fallacies-message')
  }

  async goto(): Promise<void> {
    await this.page.goto('/')
  }

  async fillAndAnalyze(text: string): Promise<void> {
    await this.textarea.fill(text)
    await this.analyzeButton.click()
  }

  async mockAnalyze(fixture: unknown): Promise<void> {
    await this.page.route('**/analyze', (route: Route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(fixture),
      })
    )
  }

  async abortAnalyze(): Promise<void> {
    await this.page.route('**/analyze', (route: Route) => route.abort('failed'))
  }

  cardConfirmed(id: string): Locator {
    return this.page.getByTestId(`card-confirmed-${id}`)
  }

  cardPossibly(id: string): Locator {
    return this.page.getByTestId(`card-possibly-${id}`)
  }

  cardMoot(id: string): Locator {
    return this.page.getByTestId(`card-moot-${id}`)
  }

  cardResolved(id: string): Locator {
    return this.page.getByTestId(`card-resolved-${id}`)
  }

  highlight(text: string): Locator {
    return this.annotatedText.getByRole('button', { name: text })
  }
}
