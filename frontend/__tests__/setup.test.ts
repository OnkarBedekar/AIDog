/**
 * Setup verification tests — checks that configs, tokens, and design system are correct.
 */

describe('Tailwind config design tokens', () => {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const tailwindConfig = require('../tailwind.config.js')
  const colors = tailwindConfig.theme?.extend?.colors ?? {}
  const shadows = tailwindConfig.theme?.extend?.boxShadow ?? {}
  const fonts = tailwindConfig.theme?.extend?.fontFamily ?? {}
  const radii = tailwindConfig.theme?.extend?.borderRadius ?? {}

  test('paper color is defined', () => {
    expect(colors.paper).toBe('#fdfbf7')
  })

  test('pencil color is defined', () => {
    expect(colors.pencil).toBe('#2d2d2d')
  })

  test('accent color is defined', () => {
    expect(colors.accent).toBe('#ff4d4d')
  })

  test('blue-pen color is defined', () => {
    expect(colors['blue-pen']).toBe('#2d5da1')
  })

  test('muted-paper color is defined', () => {
    expect(colors['muted-paper']).toBe('#e5e0d8')
  })

  test('postit color is defined', () => {
    expect(colors.postit).toBe('#fff9c4')
  })

  test('kalam font family is defined', () => {
    expect(fonts.kalam).toContain('Kalam')
  })

  test('patrick font family is defined', () => {
    expect(fonts.patrick).toContain('Patrick Hand')
  })

  test('hard shadow is defined', () => {
    expect(shadows.hard).toBe('4px 4px 0px 0px #2d2d2d')
  })

  test('hard-lg shadow is defined', () => {
    expect(shadows['hard-lg']).toBe('8px 8px 0px 0px #2d2d2d')
  })

  test('wobbly border-radius is defined', () => {
    expect(radii.wobbly).toBeDefined()
    expect(radii.wobbly).toContain('255px')
  })

  test('tailwind content paths include src/app and src/components', () => {
    const content: string[] = tailwindConfig.content ?? []
    const joined = content.join(' ')
    expect(joined).toContain('src/app')
    expect(joined).toContain('src/components')
  })

  test('no darkMode class config (light hand-drawn theme)', () => {
    expect(tailwindConfig.darkMode).toBeUndefined()
  })
})

describe('Next.js metadata', () => {
  test('layout exports metadata with correct title', async () => {
    // Dynamically import to check metadata export without rendering
    const mod = await import('../src/app/layout')
    // layout.tsx exports metadata as a named export
    expect((mod as any).metadata).toBeDefined()
    expect((mod as any).metadata.title).toContain('AIDog')
  })
})

describe('Environment', () => {
  test('NODE_ENV is defined', () => {
    expect(process.env.NODE_ENV).toBeDefined()
  })

  test('jest is running in jsdom environment', () => {
    expect(typeof window).toBe('object')
    expect(typeof document).toBe('object')
  })

  test('localStorage is available in test environment', () => {
    localStorage.setItem('test_key', 'test_value')
    expect(localStorage.getItem('test_key')).toBe('test_value')
    localStorage.removeItem('test_key')
  })
})
