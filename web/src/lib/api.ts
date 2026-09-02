const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || ''

export type Role = 'admin' | 'faculty' | 'student'

export type LoginResult = {
  access_token: string
  token_type: string
  role: Role
  username: string
}

type RequestOptions = {
  method?: string
  token?: string | null
  body?: unknown
  form?: Record<string, string>
}

export class ApiError extends Error {
  status: number
  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = {}
  if (options.token) headers.Authorization = `Bearer ${options.token}`

  let body: BodyInit | undefined
  if (options.form) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    body = new URLSearchParams(options.form)
  } else if (options.body !== undefined) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(options.body)
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method: options.method || 'GET',
    headers,
    body,
  })

  let data: unknown = null
  const text = await response.text()
  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      throw new ApiError(text || 'Unexpected server response', response.status)
    }
  }

  if (!response.ok) {
    const detail =
      typeof data === 'object' && data && 'detail' in data
        ? String((data as { detail: unknown }).detail)
        : `Request failed (${response.status})`
    throw new ApiError(detail, response.status)
  }

  return data as T
}

export const api = {
  login: (username: string, password: string) =>
    request<LoginResult>('/api/auth/login', {
      method: 'POST',
      form: { username, password },
    }),
  get: <T>(path: string, token: string) => request<T>(path, { token }),
  post: <T>(path: string, token: string, body: unknown) =>
    request<T>(path, { method: 'POST', token, body }),
  patch: <T>(path: string, token: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', token, body }),
  postPublic: <T>(path: string, body: unknown) => request<T>(path, { method: 'POST', body }),
  delete: <T>(path: string, token: string) => request<T>(path, { method: 'DELETE', token }),
  download: async (path: string, token: string, filename: string) => {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!response.ok) {
      let detail = `Download failed (${response.status})`
      try {
        const data = await response.json()
        if (data?.detail) detail = String(data.detail)
      } catch {
        /* ignore */
      }
      throw new ApiError(detail, response.status)
    }
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = filename
    document.body.appendChild(anchor)
    anchor.click()
    anchor.remove()
    URL.revokeObjectURL(url)
  },
}
