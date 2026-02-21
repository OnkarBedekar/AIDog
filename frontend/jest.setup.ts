import '@testing-library/jest-dom'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
  usePathname: () => '/home',
  redirect: jest.fn(),
}))

// Mock next/font/google
jest.mock('next/font/google', () => ({
  Kalam: () => ({ className: 'mock-kalam' }),
  Patrick_Hand: () => ({ className: 'mock-patrick' }),
  Inter: () => ({ className: 'mock-inter' }),
}))

// Silence console.error for expected React warnings in tests
const originalError = console.error
beforeAll(() => {
  console.error = (...args: any[]) => {
    if (typeof args[0] === 'string' && args[0].includes('Warning:')) return
    originalError(...args)
  }
})
afterAll(() => {
  console.error = originalError
})
