import { useEffect } from 'react'
import { ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'

/** Clears session and sends user to login when API returns 401. */
export function useApiGuard() {
  const { logout } = useAuth()

  useEffect(() => {
    const onUnhandled = (event: PromiseRejectionEvent) => {
      const reason = event.reason
      if (reason instanceof ApiError && reason.status === 401) {
        logout()
        window.location.assign('/login')
      }
    }
    window.addEventListener('unhandledrejection', onUnhandled)
    return () => window.removeEventListener('unhandledrejection', onUnhandled)
  }, [logout])

  return async function guarded<T>(fn: () => Promise<T>): Promise<T | null> {
    try {
      return await fn()
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        logout()
        window.location.assign('/login')
        return null
      }
      throw err
    }
  }
}
