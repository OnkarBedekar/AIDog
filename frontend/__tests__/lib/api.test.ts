/**
 * Tests for ApiClient — constructor, token management, and method signatures.
 */
import { ApiClient } from '@/lib/api'

// Mock global fetch
global.fetch = jest.fn()

const mockFetch = global.fetch as jest.Mock

beforeEach(() => {
  mockFetch.mockReset()
  localStorage.clear()
})

describe('ApiClient constructor', () => {
  test('instantiates with default base URL', () => {
    const client = new ApiClient()
    expect(client).toBeDefined()
  })

  test('instantiates with custom base URL', () => {
    const client = new ApiClient('http://custom-api.example.com/api')
    expect(client).toBeDefined()
  })
})

describe('ApiClient token management', () => {
  test('setToken stores token in localStorage', () => {
    const client = new ApiClient()
    client.setToken('my-jwt-token')
    expect(localStorage.getItem('token')).toBe('my-jwt-token')
  })

  test('setToken(null) removes token from localStorage', () => {
    const client = new ApiClient()
    localStorage.setItem('token', 'existing-token')
    client.setToken(null)
    expect(localStorage.getItem('token')).toBeNull()
  })

  test('token is included in Authorization header when set', async () => {
    const client = new ApiClient('http://localhost:8000/api')
    client.setToken('test-bearer-token')

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'ok' }),
    } as Response)

    await client.get('/health')

    const [, options] = mockFetch.mock.calls[0]
    expect(options.headers['Authorization']).toBe('Bearer test-bearer-token')
  })

  test('no Authorization header when token is absent', async () => {
    const client = new ApiClient('http://localhost:8000/api')
    localStorage.removeItem('token')

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ status: 'ok' }),
    } as Response)

    await client.get('/health')

    const [, options] = mockFetch.mock.calls[0]
    expect(options.headers['Authorization']).toBeUndefined()
  })
})

describe('ApiClient HTTP methods', () => {
  let client: ApiClient

  beforeEach(() => {
    client = new ApiClient('http://localhost:8000/api')
  })

  test('get() sends GET request to correct URL', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    } as Response)

    await client.get('/incidents')

    const [url, options] = mockFetch.mock.calls[0]
    expect(url).toBe('http://localhost:8000/api/incidents')
    expect(options.method).toBe('GET')
  })

  test('post() sends POST request with JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ token: 'abc', user: {} }),
    } as Response)

    await client.post('/auth/login', { email: 'a@b.com', password: 'x' })

    const [url, options] = mockFetch.mock.calls[0]
    expect(url).toBe('http://localhost:8000/api/auth/login')
    expect(options.method).toBe('POST')
    expect(options.body).toBe(JSON.stringify({ email: 'a@b.com', password: 'x' }))
    expect(options.headers['Content-Type']).toBe('application/json')
  })

  test('post() with no body sends no body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    } as Response)

    await client.post('/some/endpoint')

    const [, options] = mockFetch.mock.calls[0]
    expect(options.body).toBeUndefined()
  })

  test('get() throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ detail: 'Not found' }),
    } as Response)

    await expect(client.get('/nonexistent')).rejects.toThrow('Not found')
  })

  test('get() throws with fallback message if no JSON detail', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => { throw new Error('no json') },
    } as Response)

    await expect(client.get('/broken')).rejects.toThrow()
  })

  test('apiClient singleton is an ApiClient instance', () => {
    const { apiClient } = require('@/lib/api')
    expect(apiClient).toBeInstanceOf(ApiClient)
  })
})

describe('ApiClient 401 handling', () => {
  test('clears token on 401 response', async () => {
    const client = new ApiClient('http://localhost:8000/api')
    client.setToken('stale-token')

    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Unauthorized' }),
    } as Response)

    // Suppress window.location redirect
    const mockLocation = { href: '' }
    Object.defineProperty(window, 'location', { value: mockLocation, writable: true })

    try {
      await client.get('/api/home/overview')
    } catch {
      // expected to throw
    }

    expect(localStorage.getItem('token')).toBeNull()
  })
})
