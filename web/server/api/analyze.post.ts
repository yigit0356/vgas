import { readFileSync } from 'fs'
import { GoogleGenerativeAI } from '@google/generative-ai'
import { ElevenLabsClient } from 'elevenlabs'
import {
    defineEventHandler,
    readMultipartFormData,
    sendStream,
    createError
} from 'h3'

const prompt = readFileSync('prompts/analyze.md', 'utf8')
const model = new GoogleGenerativeAI(
    process.env.GEMINI_API_KEY
).getGenerativeModel({
    model: 'gemini-3-flash-preview'
})
const elevenLabs = new ElevenLabsClient()

export default defineEventHandler(async (event) => {
    try {
        const formData = await readMultipartFormData(event)
        const imageFile = formData?.find((item) => item.name === 'file')

        if (!imageFile || !imageFile.data || !imageFile.type) {
            throw createError({
                statusCode: 400,
                message: 'Image file not found.'
            })
        }

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
            resultText = result.response.text()

            if (!resultText)
                throw new Error('The AI returned an empty response.')
        } catch (error) {
            throw createError({
                statusCode: 502,
                message: 'An error occurred while analyzing the image.'
            })
        }

        try {
            const audioStream = await elevenLabs.textToSpeech.convert(
                'pNInz6obpgDQGcFmaJgB',
                {
                    text: resultText,
                    model_id: 'eleven_multilingual_v2',
                    output_format: 'mp3_44100_128'
                }
            )

            event.node.res.setHeader('Content-Type', 'audio/mpeg')

            return sendStream(event, audioStream)
        } catch (audioError) {
            throw createError({
                statusCode: 502,
                message: 'An error occurred while generating sound.'
            })
        }
    } catch (error) {
        if (error instanceof Error) {
            throw createError({
                statusCode: 500,
                message: error.message
            })
        }

        throw createError({
            statusCode: 500,
            message: 'An unexpected error occurred.'
        })
    }
})
