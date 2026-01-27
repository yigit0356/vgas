<script setup lang="ts">
useHead({
    title: 'VGAS | The Vision-to-Voice Protocol',
    link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap' }
    ]
})
</script>

<template>
    <div class="fixed inset-0 bg-black text-white font-['Inter',sans-serif] overflow-hidden selection:bg-white selection:text-black">
        <!-- Vercel-style Background -->
        <div class="absolute inset-0 z-0 overflow-hidden">
            <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_-20%,#111,transparent)]"></div>
            <!-- Subtle Mesh Grid -->
            <div class="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:64px_64px]"></div>
            <!-- Center Bloom -->
            <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-emerald-500/5 rounded-full blur-[120px]"></div>
        </div>

        <!-- Content Layout -->
        <div class="relative z-10 h-full flex flex-col items-center justify-between py-16 px-6">
            <!-- Top Navigation (Minimalist) -->
            <header class="w-full max-w-5xl flex justify-between items-center opacity-0 animate-in-fade-down">
                <div class="flex items-center gap-3">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L2 22H22L12 2Z" fill="white"/>
                    </svg>
                    <span class="text-sm font-semibold tracking-tight">VGAS Protocol</span>
                </div>
                <div class="flex items-center gap-6">
                    <div class="flex items-center gap-2 px-3 py-1 bg-neutral-900 border border-neutral-800 rounded-full">
                        <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
                        <span class="text-[10px] font-medium text-neutral-400 uppercase tracking-widest">Mainnet Live</span>
                    </div>
                </div>
            </header>

            <!-- Hero Section -->
            <main class="text-center space-y-8 max-w-3xl">
                <div class="inline-block px-4 py-1.5 mb-2 bg-white/5 border border-white/10 rounded-full opacity-0 animate-in-fade-up">
                    <span class="text-[11px] font-medium text-neutral-300 uppercase tracking-[0.2em] italic">Building the auditory frontier</span>
                </div>
                
                <h1 class="text-5xl md:text-7xl font-bold tracking-tighter leading-[1.1] text-transparent bg-clip-text bg-gradient-to-b from-white to-neutral-500 opacity-0 animate-in-fade-up delay-150">
                    Smarter vision.<br/>Humanized voice.
                </h1>
                
                <p class="text-lg md:text-xl text-neutral-400 max-w-xl mx-auto leading-relaxed font-light opacity-0 animate-in-fade-up delay-300">
                    The infrastructure for transforming visual sensory data into high-fidelity narrated experiences. Bridging machine perception and human semantics.
                </p>

                <!-- Status Panel (Cal.com style component) -->
                <div class="mt-12 p-1 bg-gradient-to-b from-white/10 to-transparent rounded-2xl opacity-0 animate-in-fade-up delay-500">
                    <div class="bg-[#050505] border border-white/5 rounded-[14px] p-6 flex items-center gap-8 shadow-2xl">
                        <div v-for="stat in [
                            { l: 'Vision', v: 'Gemini 1.5' },
                            { l: 'Synthesis', v: 'ElevenLabs' },
                            { l: 'Latency', v: '2.4s' }
                        ]" :key="stat.l" class="text-left border-r border-white/5 pr-8 last:border-0 last:pr-0">
                            <div class="text-[10px] text-neutral-500 font-bold uppercase tracking-widest mb-1">{{ stat.l }}</div>
                            <div class="text-sm font-semibold text-neutral-200">{{ stat.v }}</div>
                        </div>
                    </div>
                </div>
            </main>

            <!-- Bottom Detail -->
            <footer class="w-full max-w-5xl flex justify-center opacity-0 animate-in-fade-up delay-700">
                <div class="text-[11px] text-neutral-600 font-medium tracking-widest uppercase">
                    VGAS PROTOCOL — SECURE — DECENTRALIZED — AUTOMATED
                </div>
            </footer>
        </div>
    </div>
</template>

<style>
@keyframes fade-down {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes fade-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-in-fade-down {
    animation: fade-down 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-in-fade-up {
    animation: fade-up 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.delay-150 { animation-delay: 150ms; }
.delay-300 { animation-delay: 300ms; }
.delay-500 { animation-delay: 500ms; }
.delay-700 { animation-delay: 700ms; }
</style>
