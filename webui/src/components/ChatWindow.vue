<script setup>
import { ref, onMounted, watch, nextTick } from "vue";
import { chatApi } from "../services/api";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import DynamicForm from "./DynamicForm.vue";
import { useToast } from "primevue/usetoast";

const props = defineProps({
  chatId: { type: String, required: true },
});
const emit = defineEmits(["messageSent"]);

const toast = useToast();
const messages = ref([]);
const userInput = ref("");
const loading = ref(false);
const scrollContainer = ref(null);
const isNewChat = ref(true);

const fetchHistory = async () => {
  if (!props.chatId) return;
  try {
    const res = await chatApi.getHistory(props.chatId);
    messages.value = res.data;
    // If history is empty, it's a new chat and its title needs updating on first message
    isNewChat.value = messages.value.length === 0;
    scrollToBottom();
  } catch (e) {
    console.error(e);
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
    }
  });
};

const sendMessage = async () => {
  if (!userInput.value.trim() || loading.value) return;

  const query = userInput.value;
  const wasNewChat = isNewChat.value;
  userInput.value = "";

  // Add user message locally for instant feedback
  messages.value.push({
    role: "user",
    content: query,
    created_at: new Date().toISOString(),
  });
  scrollToBottom();

  loading.value = true;
  try {
    const res = await chatApi.analyze(query, props.chatId);
    // Refresh history to get the saved assistant response
    await fetchHistory();

    // Only trigger sidebar refresh if it was the first message
    if (wasNewChat) {
      emit("messageSent");
      isNewChat.value = false;
    }
  } catch (e) {
    toast.add({
      severity: "error",
      summary: "Error",
      detail: "Failed to send message",
      life: 3000,
    });
  } finally {
    loading.value = false;
  }
};

const handleFormSubmit = async (formData, originalQuery) => {
  loading.value = true;
  try {
    const res = await chatApi.execute(originalQuery, formData, props.chatId);
    // Execution results are saved to history by backend
    await fetchHistory();
  } catch (e) {
    toast.add({
      severity: "error",
      summary: "Error",
      detail: "Execution failed",
      life: 3000,
    });
  } finally {
    loading.value = false;
  }
};

const findOriginalQuery = (index) => {
  // Find the closest previous user message
  for (let i = index - 1; i >= 0; i--) {
    if (messages.value[i].role === "user") return messages.value[i].content;
  }
  return "";
};

watch(() => props.chatId, fetchHistory);
onMounted(fetchHistory);
</script>

<template>
  <div class="flex flex-column h-full">
    <!-- Messages Area -->
    <div
      ref="scrollContainer"
      class="flex-1 overflow-y-auto p-4 flex flex-column gap-3 custom-scrollbar bg-gray-50"
    >
      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="flex flex-column"
        :class="msg.role === 'user' ? 'align-items-end' : 'align-items-start'"
      >
        <div
          class="max-w-30rem p-3 border-round-xl shadow-1"
          :class="
            msg.role === 'user'
              ? 'bg-primary text-white border-noround-right'
              : 'bg-white text-900 border-noround-left border-100'
          "
        >
          <!-- Text Content -->
          <div
            v-if="typeof msg.content === 'string'"
            class="white-space-pre-wrap"
          >
            {{ msg.content }}
          </div>

          <!-- UI Components Content (Analyze Response) -->
          <div v-else-if="msg.content.components || msg.content.message">
            <div v-if="msg.content.message" class="mb-2">
              {{ msg.content.message }}
            </div>
            <DynamicForm
              v-if="msg.content.components && msg.content.components.length > 0"
              :components="msg.content.components"
              @submit="
                (data) => handleFormSubmit(data, findOriginalQuery(index))
              "
            />
          </div>
        </div>
        <div class="text-xs text-400 mt-1 px-1">
          {{ new Date(msg.created_at).toLocaleTimeString() }}
        </div>
      </div>
      <div v-if="loading" class="text-xs text-500 italic">
        AI is thinking...
      </div>
    </div>

    <!-- Input Area -->
    <div class="p-3 border-top-1 border-200 bg-white shadow-2">
      <div class="flex gap-2">
        <InputText
          v-model="userInput"
          placeholder="Type your message..."
          class="flex-1"
          @keydown.enter="sendMessage"
          :disabled="loading"
        />
        <Button icon="pi pi-send" @click="sendMessage" :loading="loading" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e9ecef;
  border-radius: 3px;
}
</style>
