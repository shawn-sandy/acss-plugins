import type { Preview } from '@storybook/react-vite'

const preview: Preview = {
  parameters: {
    a11y: {
      // axe-playwright runs against the rendered DOM; this configures
      // the addon panel for interactive Storybook usage.
      element: '#storybook-root',
      manual: false,
    },
  },
}

export default preview
