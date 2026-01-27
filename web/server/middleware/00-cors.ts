import { defineEventHandler, setResponseHeader, isMethod } from 'h3'

export default defineEventHandler((event) => {
    // Enable CORS for all API routes
    if (event.path.startsWith('/api/')) {
        setResponseHeader(event, 'Access-Control-Allow-Origin', '*')
        setResponseHeader(event, 'Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        setResponseHeader(event, 'Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
        // Handle preflight requests
        if (isMethod(event, 'OPTIONS')) {
            event.node.res.statusCode = 204
            event.node.res.statusMessage = 'No Content'
            return ''
        }
    }
})
