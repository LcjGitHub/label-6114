import { createRouter, createWebHistory } from 'vue-router'
import ExchangeList from '@/views/ExchangeList.vue'
import ExchangeForm from '@/views/ExchangeForm.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'list', component: ExchangeList },
    { path: '/new', name: 'create', component: ExchangeForm },
    { path: '/edit/:id', name: 'edit', component: ExchangeForm, props: true },
  ],
})

export default router
