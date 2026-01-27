import { defineEventHandler, getQuery, createError } from 'h3'
import { cancelRequest } from '../../utils/requestManager'

export default defineEventHandler(async (event) => {
    const { id } = getQuery(event)

    if (!id || typeof id !== 'string') {
        throw createError({
            statusCode: 400,
            message: 'Missing or invalid request ID'
        })
    }

    const cancelled = cancelRequest(id)

    return {
        success: true,
        cancelled,
        message: cancelled
            ? `Request ${id} cancelled`
            : `Request ${id} not found or already finished`
    }
})
