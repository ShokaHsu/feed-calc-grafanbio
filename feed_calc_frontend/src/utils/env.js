// src/utils/env.js

// Desktop: Tauri v2 wraps the app (standalone, no login required)
export const isDesktopApp = () => {
  return import.meta.env.VITE_IS_DESKTOP === 'true'
}

// Mobile: Capacitor wraps the app (login required, connects to Railway)
export const isMobileApp = () => {
  if (typeof window === 'undefined') return false
  return window.Capacitor?.isNativePlatform?.() === true
}

// Cloud: plain browser — Vercel-hosted SPA (login required, connects to Railway)
export const isCloudApp = () => !isDesktopApp() && !isMobileApp()

// 'desktop' | 'mobile' | 'cloud'
export const getPlatform = () => {
  if (isDesktopApp()) return 'desktop'
  if (isMobileApp()) return 'mobile'
  return 'cloud'
}