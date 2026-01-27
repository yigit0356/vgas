<script setup lang="ts">
const activeTab = ref('prompts')
const loading = ref(true)
const data = ref<any>(null)
const editingItem = ref<any>(null)
const isCreating = ref(false)
const isMobileMenuOpen = ref(false)

useHead({
    title: 'Console – VGAS Protocol',
    link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap' }
    ]
})

async function fetchData() {
    try {
        data.value = await $fetch('/api/admin/configs')
    } catch (e) {
        console.error('Failed to fetch configs', e)
    } finally {
        loading.value = false
    }
}

onMounted(async () => {
    const { authenticated } = await $fetch('/api/auth/session')
    if (!authenticated) {
        navigateTo('/auth/login')
        return
    }
    await fetchData()
})

const tabs = [
    { id: 'prompts', name: 'System Prompts', icon: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z', type: 'prompt' },
    { id: 'serviceKeys', name: 'Service API Keys', icon: 'M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z', type: 'serviceKey' },
    { id: 'appKeys', name: 'App API Keys', icon: 'M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z', type: 'appKey' },
    { id: 'versions', name: 'App Versions', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z', type: 'version' },
]

const currentItems = computed(() => {
    if (!data.value) return []
    return data.value[activeTab.value] || []
})

async function performAction(type: string, action: string, itemData: any) {
    try {
        await $fetch('/api/admin/configs', {
            method: 'POST',
            body: { type, action, data: itemData }
        })
        await fetchData()
        editingItem.value = null
    } catch (e: any) {
        alert(e.data?.message || 'Operation failed')
    }
}

function startEdit(item: any) {
    editingItem.value = { ...item }
    isCreating.value = false
}

function startCreate() {
    const tab = tabs.find(t => t.id === activeTab.value)
    if (tab?.id === 'prompts') editingItem.value = { name: '', content: '' }
    if (tab?.id === 'serviceKeys') editingItem.value = { name: '', key: '' }
    if (tab?.id === 'appKeys') editingItem.value = { key: 'vgas-' + Math.random().toString(36).substring(2, 6).toUpperCase() + '-' + Date.now().toString(36), name: '', isActive: true }
    if (tab?.id === 'versions') editingItem.value = { version: '', releaseNotes: '', isCurrent: false }
    isCreating.value = true
}

async function handleLogout() {
    await $fetch('/api/auth/logout', { method: 'POST' })
    navigateTo('/auth/login')
}

const toggleMobileMenu = () => isMobileMenuOpen.value = !isMobileMenuOpen.value
const selectTab = (id: string) => {
    activeTab.value = id
    isMobileMenuOpen.value = false
}
</script>

<template>
    <div class="min-h-screen bg-black text-white font-['Inter',sans-serif] flex flex-col lg:flex-row overflow-x-hidden selection:bg-white selection:text-black">
        <!-- Mobile Header -->
        <header class="lg:hidden flex items-center justify-between p-4 border-b border-white/5 bg-black sticky top-0 z-40">
            <div class="flex items-center gap-3">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 22H22L12 2Z" fill="white"/>
                </svg>
                <span class="font-bold tracking-tight text-sm uppercase italic font-['Space_Grotesk']">VGAS Console</span>
            </div>
            <button @click="toggleMobileMenu" class="p-2 text-neutral-400">
                <svg v-if="!isMobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 12h16m-7 6h7"/>
                </svg>
                <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>
        </header>

        <!-- Sidebar -->
        <aside 
            class="w-64 border-r border-white/5 p-6 flex flex-col fixed h-full bg-black z-40 transition-transform duration-300 lg:translate-x-0"
            :class="isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'"
        >
            <div class="hidden lg:flex items-center gap-3 mb-12 px-2">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 22H22L12 2Z" fill="white"/>
                </svg>
                <span class="font-bold tracking-widest text-xs uppercase italic font-['Space_Grotesk']">VGAS Console</span>
            </div>

            <nav class="flex-1 space-y-1">
                <div class="text-[9px] font-bold text-neutral-600 uppercase tracking-[0.2em] mb-4 px-3">Management</div>
                <button 
                    v-for="tab in tabs" 
                    :key="tab.id"
                    @click="selectTab(tab.id)"
                    :class="[
                        'w-full flex items-center gap-3 px-3 py-2.5 text-[13px] font-medium rounded-xl transition-all',
                        activeTab === tab.id ? 'bg-white/10 text-white shadow-[inset_0_0_0_1px_rgba(255,255,255,0.1)]' : 'text-neutral-500 hover:text-neutral-200'
                    ]"
                >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" :d="tab.icon"/>
                    </svg>
                    {{ tab.name }}
                </button>
            </nav>

            <div class="mt-auto pt-6 border-t border-white/5">
                <button @click="handleLogout" class="w-full flex items-center gap-3 px-3 py-2 text-[13px] font-medium text-neutral-600 hover:text-red-400 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                    </svg>
                    Logout System
                </button>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 lg:ml-64 bg-black min-h-screen">
            <!-- Content Header -->
            <div class="sticky top-0 z-30 bg-black/80 backdrop-blur-md border-b border-white/5 px-6 lg:px-10 py-6">
                <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div>
                        <h1 class="text-xl font-semibold tracking-tight">{{ tabs.find(t => t.id === activeTab)?.name }}</h1>
                        <p class="text-[11px] text-neutral-500 uppercase tracking-widest mt-1">Infrastructure Configuration</p>
                    </div>
                    <button 
                        @click="startCreate"
                        class="bg-white text-black text-xs font-bold px-5 py-2.5 rounded-xl hover:bg-neutral-200 transition-all shadow-lg active:scale-95"
                    >
                        Add Record
                    </button>
                </div>
            </div>

            <div class="p-6 lg:p-10">
                <div v-if="loading" class="flex items-center justify-center py-20">
                    <span class="w-6 h-6 border-2 border-white/10 border-t-white rounded-full animate-spin"></span>
                </div>

                <div v-else class="grid grid-cols-1 xl:grid-cols-2 gap-6 animate-in-fade">
                    <div 
                        v-for="item in currentItems" 
                        :key="item.id" 
                        class="group bg-neutral-900/40 border border-white/5 rounded-2xl p-6 hover:bg-neutral-900/60 hover:border-white/10 transition-all duration-300"
                    >
                        <div class="flex justify-between items-start mb-6">
                            <div>
                                <h3 class="font-semibold text-sm text-neutral-200 group-hover:text-white transition-colors">{{ item.name || item.version || item.key }}</h3>
                                <p class="text-[9px] text-neutral-600 font-bold uppercase tracking-widest mt-1">ID: {{ item.id.split('-')[0] }}•••</p>
                            </div>
                            <div class="flex items-center gap-2 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 transition-opacity">
                                <button @click="startEdit(item)" class="p-2 text-neutral-500 hover:text-white hover:bg-white/5 rounded-lg transition-all">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/>
                                    </svg>
                                </button>
                                <button @click="performAction(tabs.find(t=>t.id===activeTab)!.type, 'delete', {id: item.id})" class="p-2 text-neutral-500 hover:text-red-400 hover:bg-red-400/5 rounded-lg transition-all">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                    </svg>
                                </button>
                            </div>
                        </div>

                        <div class="text-[12px] text-neutral-500 bg-black/40 rounded-xl p-4 font-mono line-clamp-3 mb-6 border border-white/5 min-h-[80px]">
                            {{ item.content || item.key || item.releaseNotes }}
                        </div>

                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <div v-if="activeTab !== 'serviceKeys' && item.isActive !== undefined" 
                                     :class="['flex items-center gap-2 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest border', 
                                              item.isActive ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' : 'bg-neutral-800 text-neutral-500 border-white/5']">
                                    <div :class="['w-1 h-1 rounded-full', item.isActive ? 'bg-emerald-500 animate-pulse' : 'bg-neutral-600']"></div>
                                    {{ item.isActive ? 'Live' : 'Off' }}
                                </div>
                                <div v-if="item.isCurrent" class="text-[9px] bg-white text-black font-bold uppercase tracking-widest px-2 py-0.5 rounded-full">Current</div>
                            </div>
                            <span v-if="item.updatedAt" class="text-[9px] font-bold text-neutral-700 uppercase tracking-widest">
                                {{ new Date(item.updatedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-if="!loading && currentItems.length === 0" class="flex flex-col items-center justify-center py-32 border border-dashed border-white/5 rounded-3xl">
                    <p class="text-neutral-600 text-[11px] font-bold uppercase tracking-[0.2em]">Storage initialized — No records found</p>
                </div>
            </div>
        </main>

        <!-- Modal -->
        <Transition name="modal">
            <div v-if="editingItem" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                <div class="bg-black border border-white/10 rounded-[32px] w-full max-w-2xl overflow-hidden shadow-[0_0_100px_rgba(0,0,0,0.8)] flex flex-col max-h-[90vh] animate-modal-in">
                    <div class="px-8 py-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                        <div>
                            <h2 class="text-lg font-semibold tracking-tight">{{ isCreating ? 'New Protocol Entry' : 'Update Record' }}</h2>
                            <p class="text-[10px] text-neutral-500 uppercase tracking-widest mt-0.5">{{ activeTab }} schema</p>
                        </div>
                        <button @click="editingItem = null" class="p-2 text-neutral-500 hover:text-white hover:bg-white/5 rounded-xl transition-all">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="p-8 space-y-8 overflow-y-auto custom-scrollbar flex-1">
                        <template v-if="activeTab === 'prompts'">
                            <div class="space-y-1.5">
                                <label class="text-[10px] font-bold text-neutral-500 uppercase tracking-widest pl-1">NAME</label>
                                <input v-model="editingItem.name" class="w-full bg-neutral-900 border border-white/10 rounded-2xl px-5 py-3.5 text-sm focus:outline-none focus:border-white/20 focus:ring-1 focus:ring-white transition-all">
                            </div>
                            <div class="space-y-1.5">
                                <label class="text-[10px] font-bold text-neutral-500 uppercase tracking-widest pl-1">CONTENT</label>
                                <textarea v-model="editingItem.content" rows="12" class="w-full bg-neutral-900 border border-white/10 rounded-2xl px-5 py-3.5 text-sm focus:outline-none focus:border-white/20 focus:ring-1 focus:ring-white transition-all font-mono custom-scrollbar min-h-[300px] leading-relaxed"></textarea>
                            </div>
                        </template>

                        <template v-if="activeTab === 'serviceKeys' || activeTab === 'appKeys'">
                            <div v-if="editingItem.name !== undefined" class="space-y-1.5">
                                <label class="text-[10px] font-bold text-neutral-500 uppercase tracking-widest pl-1">NAME</label>
                                <input v-model="editingItem.name" class="w-full bg-neutral-900 border border-white/10 rounded-2xl px-5 py-3.5 text-sm focus:outline-none focus:border-white/20 transition-all">
                            </div>
                            <div class="space-y-1.5">
                                <label class="text-[10px] font-bold text-neutral-500 uppercase tracking-widest pl-1">KEY</label>
                                <input v-model="editingItem.key" class="w-full bg-neutral-900 border border-white/10 rounded-2xl px-5 py-3.5 text-sm focus:outline-none focus:border-white/20 transition-all font-mono">
                            </div>
                            <div v-if="activeTab === 'appKeys' && editingItem.description !== undefined" class="space-y-1.5">
                                <label class="text-[10px] font-bold text-neutral-500 uppercase tracking-widest pl-1">DESCRIPTION</label>
                                <input v-model="editingItem.description" class="w-full bg-neutral-900 border border-white/10 rounded-2xl px-5 py-3.5 text-sm focus:outline-none focus:border-white/20 transition-all">
                            </div>
                            <div v-if="activeTab === 'appKeys'" class="flex items-center justify-between bg-neutral-900 p-5 rounded-2xl border border-white/5">
                                <div class="space-y-0.5">
                                    <div class="text-[11px] font-bold text-neutral-200">Terminal Access</div>
                                    <div class="text-[9px] text-neutral-600 uppercase tracking-widest">Enable authentication for this key</div>
                                </div>
                                <input type="checkbox" v-model="editingItem.isActive" class="w-5 h-5 rounded-lg border-white/10 bg-black text-white focus:ring-0">
                            </div>
                        </template>

                        <template v-if="activeTab === 'versions'">
                            <div class="space-y-1.5">
                                <label class="text-[10px] font-bold text-neutral-500 uppercase tracking-widest pl-1">VERSION</label>
                                <input v-model="editingItem.version" placeholder="1.0.0" class="w-full bg-neutral-900 border border-white/10 rounded-2xl px-5 py-3.5 text-sm focus:outline-none transition-all">
                            </div>
                            <div class="space-y-1.5">
                                <label class="text-[10px] font-bold text-neutral-500 uppercase tracking-widest pl-1">RELEASE NOTES</label>
                                <textarea v-model="editingItem.releaseNotes" rows="5" class="w-full bg-neutral-900 border border-white/10 rounded-2xl px-5 py-3.5 text-sm focus:outline-none transition-all leading-relaxed"></textarea>
                            </div>
                            <div class="flex items-center justify-between bg-neutral-900 p-5 rounded-2xl border border-white/5">
                                <div class="space-y-0.5">
                                    <div class="text-[11px] font-bold text-neutral-200">Primary Version</div>
                                    <div class="text-[9px] text-neutral-600 uppercase tracking-widest">Set as the public deployment target</div>
                                </div>
                                <input type="checkbox" v-model="editingItem.isCurrent" class="w-5 h-5 rounded-lg border-white/10 bg-black text-white focus:ring-0">
                            </div>
                        </template>
                    </div>

                    <div class="px-8 py-6 border-t border-white/5 flex flex-col sm:flex-row justify-end gap-3 bg-white/[0.01]">
                        <button @click="editingItem = null" class="px-6 py-2.5 text-[11px] font-bold text-neutral-500 hover:text-white uppercase tracking-widest transition-colors">Abort</button>
                        <button @click="performAction(tabs.find(t=>t.id===activeTab)!.type, isCreating ? 'create' : 'update', editingItem)" 
                                class="bg-white text-black text-[11px] font-bold px-8 py-2.5 rounded-xl hover:bg-neutral-200 transition-all uppercase tracking-widest">
                            Commit Changes
                        </button>
                    </div>
                </div>
            </div>
        </Transition>
    </div>
</template>

<style>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
.custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

@keyframes fade-in {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes modal-in {
    from { opacity: 0; transform: scale(0.98) translateY(10px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
}

.animate-in-fade {
    animation: fade-in 0.5s ease-out forwards;
}

.animate-modal-in {
    animation: modal-in 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.modal-enter-active, .modal-leave-active {
    transition: opacity 0.3s ease;
}
.modal-enter-from, .modal-leave-to {
    opacity: 0;
}
</style>
