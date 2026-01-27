import { defineEventHandler, getQuery, createError } from 'h3'
import { getAppApiKeys } from '../utils/config'

export default defineEventHandler(async (event) => {
    if (!event.path.startsWith('/api/analyze')) {
        return
    }

    const query = getQuery(event)
    const apiKey = query.api_key as string

    const validApiKeys = await getAppApiKeys()

    if (validApiKeys.length === 0) {
        console.warn(
            'APP_API_KEY is not set in environment variables. API is currently unprotected.'
        )
        return
    }

    if (!apiKey || !validApiKeys.includes(apiKey)) {
        throw createError({
            statusCode: 401,
            statusMessage: 'Unauthorized',
            message: 'Invalid or missing API Key'
        })
    }
})
