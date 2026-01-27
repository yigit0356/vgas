import { defineEventHandler, readBody, createError } from 'h3'
import prisma from '../../utils/prisma'
import { getAllServiceApiKeys, getAllAppApiKeys, getAllSystemPrompts, getAllAppVersions } from '../../utils/config'

export default defineEventHandler(async (event) => {
    const method = event.method

    if (method === 'GET') {
        const [serviceKeys, appKeys, prompts, versions] = await Promise.all([
            getAllServiceApiKeys(),
            getAllAppApiKeys(),
            getAllSystemPrompts(),
            getAllAppVersions()
        ])

        return {
            serviceKeys,
            appKeys,
            prompts,
            versions
        }
    }

    if (method === 'POST') {
        const body = await readBody(event)
        const { type, action, data } = body

        if (!type || !action || !data) {
            throw createError({ statusCode: 400, message: 'Type, action and data are required' })
        }

        const modelMap: any = {
            serviceKey: prisma.serviceApiKey,
            appKey: prisma.appApiKey,
            prompt: prisma.systemPrompt,
            version: prisma.appVersion
        }

        const model = modelMap[type]
        if (!model) throw createError({ statusCode: 400, message: 'Invalid type' })

        try {
            switch (action) {
                case 'create':
                    return await model.create({ data })
                case 'update':
                    const { id, ...updateData } = data
                    return await model.update({ where: { id }, data: updateData })
                case 'delete':
                    return await model.delete({ where: { id: data.id } })
                default:
                    throw createError({ statusCode: 400, message: 'Invalid action' })
            }
        } catch (e: any) {
            throw createError({
                statusCode: 500,
                message: e.message || 'Database error'
            })
        }
    }
})
