import { defineEventHandler, getQuery, createError } from 'h3'

export default defineEventHandler((event) => {
    if (!event.path.startsWith('/api')) {
        return
    }

    const query = getQuery(event)
    const apiKey = query.api_key as string

    const validApiKeys =
        process.env.APP_API_KEY?.split(',').map((k: string) => k.trim()) || []

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
