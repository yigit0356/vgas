import { defineEventHandler } from 'h3'
import { getAppVersion } from '../utils/config'

export default defineEventHandler(async (event) => {
    return await getAppVersion()
})
