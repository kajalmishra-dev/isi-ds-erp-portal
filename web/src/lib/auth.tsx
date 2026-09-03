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
  tenantId: string | null
  login: (username: string, password: string) => Promise<LoginResult>
  /** Private demo sandbox: reuse this browser's world, or create a fresh copy. */
  loginDemo: (role: Role) => Promise<LoginResult>
  logout: () => void
}

const STORAGE_KEY = 'isi-erp-auth-v2'
const TENANT_KEY = 'isi-erp-tenant-v1'

const AuthContext = createContext<AuthState | null>(null)

function readTenantId(): string | null {
  try {
    return localStorage.getItem(TENANT_KEY)
  } catch {
    return null
  }
}

function persistTenant(tenantId: string | null | undefined) {
  if (!tenantId) return
  try {
    localStorage.setItem(TENANT_KEY, tenantId)
  } catch {
    /* ignore */
  }
}

function readStored(): Pick<AuthState, 'token' | 'role' | 'username' | 'tenantId'> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    const tenantId = readTenantId()
    if (!raw) return { token: null, role: null, username: null, tenantId }
    const parsed = JSON.parse(raw) as LoginResult
    if (!parsed?.access_token || !parsed?.role) {
      localStorage.removeItem(STORAGE_KEY)
      return { token: null, role: null, username: null, tenantId }
    }
    if (parsed.tenant_id) persistTenant(parsed.tenant_id)
    return {
      token: parsed.access_token,
      role: parsed.role,
      username: parsed.username,
      tenantId: parsed.tenant_id || tenantId,
    }
  } catch {
    localStorage.removeItem(STORAGE_KEY)
    return { token: null, role: null, username: null, tenantId: readTenantId() }
  }
}

function applySession(
  result: LoginResult,
  setters: {
    setToken: (v: string | null) => void
    setRole: (v: Role | null) => void
    setUsername: (v: string | null) => void
    setTenantId: (v: string | null) => void
  },
) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(result))
  localStorage.removeItem('isi-erp-auth')
  if (result.tenant_id) {
    persistTenant(result.tenant_id)
    setters.setTenantId(result.tenant_id)
  }
  setters.setToken(result.access_token)
  setters.setRole(result.role)
  setters.setUsername(result.username)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const initial = readStored()
  const [token, setToken] = useState<string | null>(initial.token)
  const [role, setRole] = useState<Role | null>(initial.role)
  const [username, setUsername] = useState<string | null>(initial.username)
  const [tenantId, setTenantId] = useState<string | null>(initial.tenantId)

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem('isi-erp-auth')
    // Keep TENANT_KEY so the same browser returns to its private sandbox.
    setToken(null)
    setRole(null)
    setUsername(null)
  }, [])

  const login = useCallback(async (user: string, password: string) => {
    const result = await api.login(user, password)
    applySession(result, { setToken, setRole, setUsername, setTenantId })
    return result
  }, [])

  const loginDemo = useCallback(async (demoRole: Role) => {
    const existing = readTenantId()
    const result = await api.demoStart(demoRole, existing)
    applySession(result, { setToken, setRole, setUsername, setTenantId })
    return result
  }, [])

  const value = useMemo(
    () => ({ token, role, username, tenantId, login, loginDemo, logout }),
    [token, role, username, tenantId, login, loginDemo, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
