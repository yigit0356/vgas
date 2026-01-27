import tailwindcss from '@tailwindcss/vite'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: '2025-07-15',
    devtools: { enabled: true },
    modules: ['@nuxt/eslint'],
    app: {
        head: {
            title: 'VGAS Protocol',
            link: [
                { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
                { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' }
            ]
        }
    },
    vite: {
        plugins: [tailwindcss()]
    },
    css: ['./app/assets/css/main.css']
})
