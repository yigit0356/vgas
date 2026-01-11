import { defineEventHandler, sendRedirect } from 'h3'

export default defineEventHandler(async (event) => {
    return await sendRedirect(event, 'https://ygtdev.vercel.app')
})
