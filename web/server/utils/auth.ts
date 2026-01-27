import { H3Event } from 'h3'

const SESSION_COOKIE_NAME = 'admin_session'

export function getAdminPassword() {
    return process.env.ADMIN_PASSWORD || 'admin'
}

export function setAdminSession(event: H3Event) {
    setCookie(event, SESSION_COOKIE_NAME, 'true', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 60 * 24 // 1 day
    })
}

export function clearAdminSession(event: H3Event) {
    deleteCookie(event, SESSION_COOKIE_NAME)
}

export function isAdminAuthenticated(event: H3Event) {
    const session = getCookie(event, SESSION_COOKIE_NAME)
    return session === 'true'
}
