import prisma from './prisma'
import { readFileSync } from 'fs'

export async function getSystemPrompt(name: string, fallbackPath?: string): Promise<string> {
    try {
        const prompt = await prisma.systemPrompt.findUnique({
            where: { name }
        })
        if (prompt) return prompt.content
    } catch (e) {
        console.error(`Error fetching prompt ${name} from DB:`, e)
    }

    if (fallbackPath) {
        try {
            return readFileSync(fallbackPath, 'utf8')
        } catch (e) {
            console.error(`Error reading fallback prompt file ${fallbackPath}:`, e)
        }
    }
    
    return ''
}

export async function getServiceApiKey(name: string): Promise<string | undefined> {
    try {
        const apiKey = await prisma.serviceApiKey.findUnique({
            where: { name, isActive: true }
        })
        if (apiKey) return apiKey.key
    } catch (e) {
        console.error(`Error fetching service key ${name} from DB:`, e)
    }

    // Fallback to runtimeConfig/env
    const config = useRuntimeConfig()
    const configKey = name.toLowerCase() + 'ApiKey'
    return (config as any)[configKey]
}

export async function getAppApiKeys(): Promise<string[]> {
    try {
        const keys = await prisma.appApiKey.findMany({
            where: { isActive: true },
            select: { key: true }
        })
        if (keys.length > 0) return keys.map((k: any) => k.key)
    } catch (e) {
        console.error('Error fetching App API keys from DB:', e)
    }

    // Fallback to runtimeConfig/env
    const config = useRuntimeConfig()
    return (config.appApiKey as string)?.split(',').map((k: string) => k.trim()) || []
}

export async function getAppVersion(): Promise<any> {
    try {
        const version = await prisma.appVersion.findFirst({
            where: { isCurrent: true }
        })
        if (version) return version
    } catch (e) {
        console.error(`Error fetching version from DB:`, e)
    }

    try {
        const versionData = JSON.parse(readFileSync('version.json', 'utf8'))
        return versionData
    } catch (e) {
        return { version: '0.0.0', error: 'No version info found' }
    }
}
