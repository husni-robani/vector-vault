import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import ChatView from './views/ChatView.vue';
import './assets/styles/main.css';

const routes = [
  { path: '/', redirect: '/chat' },
  { path: '/chat', component: ChatView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const app = createApp(App);
app.use(router);
app.mount('#app');
