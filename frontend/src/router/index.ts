import { createRouter, createWebHistory } from 'vue-router'
import ExchangeList from '@/views/ExchangeList.vue'
import ExchangeForm from '@/views/ExchangeForm.vue'
import ExchangeDetail from '@/views/ExchangeDetail.vue'
import Overview from '@/views/Overview.vue'
import ContactList from '@/views/ContactList.vue'
import ContactForm from '@/views/ContactForm.vue'
import ContactDetail from '@/views/ContactDetail.vue'
import TrendAnalysis from '@/views/TrendAnalysis.vue'
import LabelList from '@/views/LabelList.vue'
import LabelForm from '@/views/LabelForm.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'overview', component: Overview },
    { path: '/trend', name: 'trend', component: TrendAnalysis },
    { path: '/list', name: 'list', component: ExchangeList },
    { path: '/new', name: 'create', component: ExchangeForm },
    { path: '/edit/:id', name: 'edit', component: ExchangeForm, props: true },
    { path: '/detail/:id', name: 'detail', component: ExchangeDetail, props: true },
    { path: '/contacts', name: 'contacts', component: ContactList },
    { path: '/contacts/new', name: 'contact-create', component: ContactForm },
    { path: '/contacts/edit/:id', name: 'contact-edit', component: ContactForm, props: true },
    { path: '/contacts/detail/:id', name: 'contact-detail', component: ContactDetail, props: true },
    { path: '/labels', name: 'labels', component: LabelList },
    { path: '/labels/new', name: 'label-create', component: LabelForm },
    { path: '/labels/edit/:id', name: 'label-edit', component: LabelForm, props: true },
  ],
})

export default router
