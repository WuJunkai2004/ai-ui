<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { authApi } from '../services/api';
import Card from 'primevue/card';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import Toast from 'primevue/toast';
import { useToast } from 'primevue/usetoast';

const router = useRouter();
const toast = useToast();
const username = ref('');
const password = ref('');
const loading = ref(false);

const handleLogin = async () => {
    if (!username.value || !password.value) {
        toast.add({ severity: 'warn', summary: 'Warning', detail: 'Please fill in all fields', life: 3000 });
        return;
    }

    loading.value = true;
    try {
        const res = await authApi.login(username.value, password.value);
        const { token } = res.data;
        sessionStorage.setItem('auth_token', token);
        sessionStorage.setItem('username', username.value);
        router.push('/');
    } catch (error) {
        toast.add({ severity: 'error', summary: 'Login Failed', detail: 'Invalid credentials', life: 3000 });
    } finally {
        loading.value = false;
    }
};
</script>

<template>
  <div class="flex align-items-center justify-content-center min-h-screen surface-ground">
    <Toast />
    <Card class="w-full md:w-30rem shadow-4">
      <template #title>
        <div class="text-center text-3xl font-bold text-primary mb-2">GenUI Agent</div>
      </template>
      <template #subtitle>
        <div class="text-center mb-4">Login to start chatting</div>
      </template>
      <template #content>
        <div class="flex flex-column gap-4">
          <div class="flex flex-column gap-2">
            <label for="username" class="font-semibold">Username</label>
            <InputText id="username" v-model="username" class="w-full" @keydown.enter="handleLogin" />
          </div>
          <div class="flex flex-column gap-2">
            <label for="password" class="font-semibold">Password</label>
            <Password id="password" v-model="password" :feedback="false" toggleMask class="w-full" inputClass="w-full" @keydown.enter="handleLogin" />
          </div>
          <Button label="Sign In" icon="pi pi-sign-in" @click="handleLogin" :loading="loading" class="w-full mt-2" />
        </div>
      </template>
    </Card>
  </div>
</template>
