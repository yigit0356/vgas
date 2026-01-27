import { GoogleGenerativeAI } from '@google/generative-ai'
import { ElevenLabsClient } from 'elevenlabs'
import {
    defineEventHandler,
    readMultipartFormData,
    sendStream,
    createError,
    getQuery
} from 'h3'
import { registerRequest, unregisterRequest } from '../../utils/requestManager'
import { getSystemPrompt, getServiceApiKey } from '../../utils/config'

export default defineEventHandler(async (event) => {
    const query = getQuery(event)
    const promptName = (query.prompt as string) || 'analyze'
    const prompt = await getSystemPrompt(promptName, 'prompts/analyze.md')
    const geminiKey = await getServiceApiKey('GEMINI')
    const elevenKey = await getServiceApiKey('ELEVENLABS')

    if (!geminiKey || !elevenKey) {
        throw createError({
            statusCode: 500,
            message: 'API Keys not configured'
        })
    }

    const model = new GoogleGenerativeAI(geminiKey).getGenerativeModel({
        model: 'gemini-3-flash-preview'
    })
    const elevenLabs = new ElevenLabsClient({
        apiKey: elevenKey
    })

    const { id } = getQuery(event)
    const requestId = id as string

    if (!requestId) {
        throw createError({
            statusCode: 400,
            message: 'Missing request ID'
        })
    }

    const abortController = registerRequest(requestId)
    const { signal } = abortController

    try {
        const formData = await readMultipartFormData(event)
        const imageFile = formData?.find((item) => item.name === 'file')

        if (!imageFile || !imageFile.data || !imageFile.type) {
            throw createError({
                statusCode: 400,
                message: 'Image file not found.'
            })
        }

        if (signal.aborted)
            throw createError({ statusCode: 499, message: 'Request Aborted' })

        let resultText = ''

        try {
            const result = await model.generateContent([
                prompt,
                {
                    inlineData: {
                        data: imageFile.data.toString('base64'),
                        mimeType: imageFile.type
                    }
                }
            ])

            if (signal.aborted)
                throw createError({
                    statusCode: 499,
                    message: 'Request Aborted'
                })

            resultText = result.response.text()

            if (!resultText)
                throw new Error('The AI returned an empty response.')
        } catch (error: any) {
            if (error.statusCode === 499) throw error
            console.error('Gemini API Error:', error)
            throw createError({
                statusCode: 502,
                message: 'An error occurred while analyzing the image.'
            })
        }

        if (signal.aborted)
            throw createError({ statusCode: 499, message: 'Request Aborted' })

        try {
            const audioStream = await elevenLabs.textToSpeech.convert(
                'pNInz6obpgDQGcFmaJgB',
                {
                    text: resultText,
                    model_id: 'eleven_multilingual_v2',
                    output_format: 'mp3_44100_128'
                }
            )

            if (signal.aborted)
                throw createError({
                    statusCode: 499,
                    message: 'Request Aborted'
                })

            event.node.res.setHeader('Content-Type', 'audio/mpeg')

            // Stop stream if request is cancelled during playback/streaming
            signal.addEventListener('abort', () => {
                event.node.res.destroy()
            })

            return sendStream(event, audioStream)
        } catch (audioError: any) {
            if (audioError.statusCode === 499) throw audioError
            console.error('ElevenLabs API Error:', audioError)
            throw createError({
                statusCode: 502,
                message: 'An error occurred while generating sound.'
            })
        }
    } catch (error: any) {
        if (error.statusCode === 499) {
            console.log(`Request ${requestId} was cancelled.`)
            return { cancelled: true }
        }

        if (error.statusCode && error.message) {
            throw error
        }

        console.error('Global Handler Error:', error)
        throw createError({
            statusCode: 500,
            message: error.message || 'An unexpected error occurred.'
        })
    } finally {
        unregisterRequest(requestId)
    }
})
