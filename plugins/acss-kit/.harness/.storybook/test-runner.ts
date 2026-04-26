// Storybook test-runner hook that injects axe-core into each story page
// and runs `checkA11y` on the rendered DOM. Without this file,
// `npm run test-storybook` only verifies that stories mount; the
// accessibility audits we advertise in the harness README would silently
// be no-ops.
import { injectAxe, checkA11y } from 'axe-playwright'
import type { TestRunnerConfig } from '@storybook/test-runner'

const config: TestRunnerConfig = {
  async preVisit(page) {
    await injectAxe(page)
  },
  async postVisit(page) {
    await checkA11y(page, '#storybook-root', {
      detailedReport: true,
      detailedReportOptions: { html: true },
    })
  },
}

export default config
