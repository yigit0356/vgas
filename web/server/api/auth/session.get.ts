import { defineEventHandler } from 'h3'
import { isAdminAuthenticated } from '../../utils/auth'

export default defineEventHandler((event) => {
    return {
        authenticated: isAdminAuthenticated(event)
    }
})
