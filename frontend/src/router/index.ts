import { createRouter, createWebHistory } from 'vue-router'
import ExchangeList from '@/views/ExchangeList.vue'
import ExchangeForm from '@/views/ExchangeForm.vue'
import Overview from '@/views/Overview.vue'
import ContactList from '@/views/ContactList.vue'
import ContactForm from '@/views/ContactForm.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'overview', component: Overview },
    { path: '/list', name: 'list', component: ExchangeList },
    { path: '/new', name: 'create', component: ExchangeForm },
    { path: '/edit/:id', name: 'edit', component: ExchangeForm, props: true },
    { path: '/contacts', name: 'contacts', component: ContactList },
    { path: '/contacts/new', name: 'contact-create', component: ContactForm },
    { path: '/contacts/edit/:id', name: 'contact-edit', component: ContactForm, props: true },
  ],
})

export default router
