import { defineEventHandler, readBody, createError } from 'h3'
import { getAdminPassword, setAdminSession } from '../../utils/auth'

export default defineEventHandler(async (event) => {
    const body = await readBody(event)
    const { password } = body

    if (password === getAdminPassword()) {
        setAdminSession(event)
        return { success: true }
    }

    throw createError({
        statusCode: 401,
        statusMessage: 'Unauthorized',
        message: 'Invalid password'
    })
})
