<script setup>
import { ref } from 'vue';
import ChatSidebar from '../components/ChatSidebar.vue';
import ChatWindow from '../components/ChatWindow.vue';
import Toast from 'primevue/toast';

const selectedChatId = ref(null);
const sidebarRef = ref(null);

const handleChatCreated = () => {
    // Refresh list if needed, but createChat in sidebar already does it
};

const refreshSidebar = () => {
    sidebarRef.value?.fetchChats();
};
</script>

<template>
    <div class="flex h-screen w-full overflow-hidden surface-ground">
        <Toast />
        <!-- Sidebar: 30% or fixed width -->
        <div class="w-full md:w-20rem lg:w-24rem h-full flex-shrink-0">
            <ChatSidebar ref="sidebarRef" v-model="selectedChatId" />
        </div>

        <!-- Main Content -->
        <div class="flex-1 h-full flex flex-column relative border-left-1 border-200">
            <div v-if="selectedChatId" class="h-full">
                <ChatWindow :chatId="selectedChatId" @messageSent="refreshSidebar" />
            </div>
            <div v-else class="h-full flex flex-column align-items-center justify-content-center text-500 bg-white">
                <i class="pi pi-comments text-6xl mb-4"></i>
                <div class="text-xl font-medium">Select a chat to start</div>
                <div class="mt-2 text-sm text-400">Or create a new one using the + button</div>
            </div>
        </div>
    </div>
</template>

<style>
:root {
    --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
}
</style>
