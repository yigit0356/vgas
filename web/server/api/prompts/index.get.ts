import { defineEventHandler } from 'h3'
import { getAllSystemPrompts } from '../../utils/config'

export default defineEventHandler(async () => {
    const prompts = await getAllSystemPrompts()
    
    // Return a simplified list for the controller
    return prompts.map(p => ({
        id: p.id,
        name: p.name,
        content: p.content,
        updatedAt: p.updatedAt
    }))
})
