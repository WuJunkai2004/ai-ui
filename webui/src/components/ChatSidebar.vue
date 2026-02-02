<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import Button from "primevue/button";
import Avatar from "primevue/avatar";
import { chatApi } from "../services/api";

const props = defineProps(["modelValue"]);
const emit = defineEmits(["update:modelValue", "refresh"]);

const router = useRouter();
const chats = ref([]);
const username = sessionStorage.getItem("username") || "User";

const fetchChats = async () => {
  try {
    const res = await chatApi.getChatList();
    chats.value = res.data;
  } catch (e) {
    console.error(e);
  }
};

const createChat = async () => {
  try {
    const res = await chatApi.createChat();
    chats.value.unshift(res.data);
    emit("update:modelValue", res.data.chatId);
  } catch (e) {
    console.error(e);
  }
};

const logout = () => {
  sessionStorage.clear();
  router.push("/login");
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString();
};

onMounted(fetchChats);

defineExpose({ fetchChats });
</script>

<template>
  <div class="flex flex-column h-full bg-white border-right-1 border-200">
    <div
      class="p-3 border-bottom-1 border-200 flex align-items-center justify-content-between"
    >
      <span class="font-bold text-xl text-900">Chats</span>
      <Button
        icon="pi pi-plus"
        text
        rounded
        aria-label="New Chat"
        @click="createChat"
        v-tooltip="'New Chat'"
      />
    </div>
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div v-if="chats.length === 0" class="p-4 text-center text-500">
        No chats yet
      </div>
      <div
        v-for="chat in chats"
        :key="chat.chatId"
        class="p-3 cursor-pointer border-bottom-1 border-100 transition-colors transition-duration-150 hover:bg-gray-100"
        :class="{ 'bg-blue-50 border-blue-200': modelValue === chat.chatId }"
        @click="$emit('update:modelValue', chat.chatId)"
      >
        <div
          class="font-medium white-space-nowrap overflow-hidden text-overflow-ellipsis text-900"
        >
          {{ chat.title || "New Chat" }}
        </div>
        <div class="text-xs text-500 mt-1">
          {{ formatDate(chat.created_at) }}
        </div>
      </div>
    </div>
    <div class="p-3 border-top-1 border-200 bg-gray-50">
      <div class="flex align-items-center gap-2">
        <Avatar
          icon="pi pi-user"
          shape="circle"
          class="bg-primary text-white"
        />
        <span class="font-medium text-900">{{ username }}</span>
        <Button
          icon="pi pi-sign-out"
          text
          rounded
          class="ml-auto text-600"
          @click="logout"
          v-tooltip="'Logout'"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #dee2e6;
  border-radius: 3px;
}
</style>
