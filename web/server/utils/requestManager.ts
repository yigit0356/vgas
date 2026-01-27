const activeRequests = new Map<string, AbortController>()

export const registerRequest = (id: string) => {
    const controller = new AbortController()
    activeRequests.set(id, controller)
    return controller
}

export const unregisterRequest = (id: string) => {
    activeRequests.delete(id)
}

export const cancelRequest = (id: string) => {
    const controller = activeRequests.get(id)
    if (controller) {
        controller.abort()
        activeRequests.delete(id)
        return true
    }
    return false
}
