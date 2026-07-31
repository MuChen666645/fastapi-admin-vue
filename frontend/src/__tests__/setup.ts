import { vi } from 'vitest'

vi.mock('lottie-web', () => ({
  default: {
    loadAnimation: vi.fn(() => ({
      destroy: vi.fn(),
      pause: vi.fn(),
      play: vi.fn(),
    })),
  },
}))
