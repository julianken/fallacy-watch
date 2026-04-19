import { render, screen } from '@testing-library/react'
import type { SpanResult } from '../../types'
import { ResolvedCard } from '../ResolvedCard'

const span = {
  id: 'span_0', text: 'All experts agree', start: 0, end: 17,
  status: 'confirmed' as const, fallacy_type: 'ad populum',
  explanation: 'Appeals to consensus.',
  challenge: {
    type: 'premise_check' as const,
    question: { text: 'Is this a stub?', yes_label: 'Yes', no_label: 'No' },
  },
  if_legitimate: null, if_fallacy: null, content_generated: true,
} satisfies SpanResult

test('displays fallacy type in Title Case', () => {
  render(<ResolvedCard span={span} outcome="CONFIRMED" />)
  expect(screen.getByText(/Ad Populum/)).toBeInTheDocument()
})
