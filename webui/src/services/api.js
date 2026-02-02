import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 30000
});

api.interceptors.request.use(config => {
    const token = sessionStorage.getItem('auth_token');
    if (token) {
        config.headers.Authorization = token;
    }
    return config;
});

api.interceptors.response.use(response => {
    return response;
}, error => {
    if (error.response && error.response.status === 401) {
        // Only redirect if not already on login page to avoid loops
        if (!window.location.pathname.includes('/login')) {
            sessionStorage.removeItem('auth_token');
            window.location.href = '/login';
        }
    }
    return Promise.reject(error);
});

export const authApi = {
    login: (username, password) => api.post('/login', { username, password })
};

export const chatApi = {
    createChat: () => api.post('/chat'),
    getChatList: () => api.get('/chatList'),
    getHistory: (chatId) => api.get('/history', { params: { chat_id: chatId, range: '[1,100]' } }),
    analyze: (query, chatId) => api.post('/analyze', { query, chat_id: chatId }),
    execute: (originalQuery, formData, chatId) => api.post('/execute', { original_query: originalQuery, form_data: formData, chat_id: chatId })
};

export default api;
