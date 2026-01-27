import { defineEventHandler, createError } from 'h3'
import { isAdminAuthenticated } from '../utils/auth'

export default defineEventHandler((event) => {
    const isApiAdmin = event.path.startsWith('/api/admin')
    const isAdminPage = event.path.startsWith('/admin')

    if (isApiAdmin || isAdminPage) {
        if (!isAdminAuthenticated(event)) {
            // If it's an API call, return 401
            if (isApiAdmin) {
                throw createError({
                    statusCode: 401,
                    statusMessage: 'Unauthorized'
                })
            }
            // If it's a page navigation, Nuxt middleware will handle the redirect on the client
            // but we can also handle it here if needed.
        }
    }
})
