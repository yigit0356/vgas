<script setup lang="ts">
const password = ref('')
const loading = ref(false)
const error = ref('')

useHead({
    title: 'Login – VGAS Protocol',
    link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap' }
    ]
})

async function handleLogin() {
    loading.value = true
    error.value = ''
    try {
        await $fetch('/api/auth/login', {
            method: 'POST',
            body: { password: password.value }
        })
        navigateTo('/admin')
    } catch (e: any) {
        error.value = e.data?.message || 'Invalid password'
    } finally {
        loading.value = false
    }
}

onMounted(async () => {
    const { authenticated } = await $fetch('/api/auth/session')
    if (authenticated) navigateTo('/admin')
})
</script>

<template>
    <div class="min-h-screen bg-black text-white flex items-center justify-center font-['Inter',sans-serif] selection:bg-white selection:text-black">
        <!-- Background Bloom -->
        <div class="absolute inset-0 z-0 bg-[radial-gradient(circle_at_50%_0%,#111,transparent)] pointer-events-none"></div>

        <div class="w-full max-w-[400px] px-6 relative z-10 animate-fade-in-up">
            <div class="mb-10 flex flex-col items-center">
                <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shadow-[0_0_30px_rgba(255,255,255,0.1)] mb-6">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 22H22L12 2Z" fill="black"/>
                    </svg>
                </div>
                <h1 class="text-2xl font-semibold tracking-tight">Admin Authentication</h1>
                <p class="text-sm text-neutral-500 mt-2">Identification required to access protocol Terminal</p>
            </div>

            <form @submit.prevent="handleLogin" class="space-y-4">
                <div class="space-y-1.5">
                    <label class="text-[10px] font-bold text-neutral-500 uppercase tracking-widest pl-1">PASSWORD</label>
                    <input 
                        v-model="password" 
                        type="password" 
                        placeholder="••••••••"
                        required
                        class="w-full bg-neutral-900 border border-neutral-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-white focus:border-white transition-all placeholder:text-neutral-700"
                    >
                </div>
                
                <div v-if="error" class="text-red-500 text-xs text-center bg-red-500/10 py-3 rounded-xl border border-red-500/20 animate-shake">
                    {{ error }}
                </div>

                <div class="pt-2">
                    <button 
                        type="submit" 
                        :disabled="loading"
                        class="w-full bg-white text-black text-sm font-semibold py-3 rounded-xl hover:bg-neutral-200 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                        <span v-if="loading" class="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin"></span>
                        {{ loading ? 'Authenticating...' : 'Enter Console' }}
                    </button>
                </div>
            </form>

            <footer class="mt-16 pt-8 border-t border-white/5 text-center">
                <NuxtLink to="/" class="text-[10px] font-bold text-neutral-600 hover:text-white transition-colors uppercase tracking-[0.2em]">Return to Site Root</NuxtLink>
            </footer>
        </div>
    </div>
</template>

<style>
@keyframes fade-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.animate-fade-in-up {
    animation: fade-up 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-shake {
    animation: shake 0.2s ease-in-out 0s 2;
}
</style>
