import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { api, type LoginResult, type Role } from './api'

type AuthState = {
  token: string | null
  role: Role | null
  username: string | null
  login: (username: string, password: string) => Promise<LoginResult>
  logout: () => void
}

const STORAGE_KEY = 'isi-erp-auth-v2'

const AuthContext = createContext<AuthState | null>(null)

function readStored(): Pick<AuthState, 'token' | 'role' | 'username'> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { token: null, role: null, username: null }
    const parsed = JSON.parse(raw) as LoginResult
    if (!parsed?.access_token || !parsed?.role) {
      localStorage.removeItem(STORAGE_KEY)
      return { token: null, role: null, username: null }
    }
    return {
      token: parsed.access_token,
      role: parsed.role,
      username: parsed.username,
    }
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return { token: null, role: null, username: null }
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const initial = readStored()
  const [token, setToken] = useState<string | null>(initial.token)
  const [role, setRole] = useState<Role | null>(initial.role)
  const [username, setUsername] = useState<string | null>(initial.username)

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY)
    // clear legacy key from earlier builds
    localStorage.removeItem('isi-erp-auth')
    setToken(null)
    setRole(null)
    setUsername(null)
  }, [])

  const login = useCallback(async (user: string, password: string) => {
    const result = await api.login(user, password)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(result))
    localStorage.removeItem('isi-erp-auth')
    setToken(result.access_token)
    setRole(result.role)
    setUsername(result.username)
    return result
  }, [])

  const value = useMemo(
    () => ({ token, role, username, login, logout }),
    [token, role, username, login, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
