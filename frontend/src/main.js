import Vue from 'vue'
import App from './App.vue'
import store from "./store/index"
import vuetify from './plugins/vuetify'
import VueRouter from "vue-router"
import PortalVue from 'portal-vue'
import VueClipboard from 'vue-clipboard2'
import i18n from "./plugins/i18n"

import router from './router'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import Toast from "vue-toastification";

import('./assets/style.css')
import '@fortawesome/fontawesome-free/css/all.css'
import '@fortawesome/fontawesome-free/js/all.js'
import "vue-toastification/dist/index.css";

VueClipboard.config.autoSetContainer = true // add this line
Vue.config.productionTip = false

Vue.use(VueRouter)
Vue.use(PortalVue)
Vue.use(VueClipboard)

const toastsOptions = {};
Vue.use(Toast, toastsOptions);

Vue.component('font-awesome-icon', FontAwesomeIcon)

Vue.filter('str_limit', function (value, size) {
  if (!value) return '';
  value = value.toString();

  if (value.length <= size) {
    return value;
  }
  return value.substr(0, size) + '...';
});

new Vue({
  vuetify,
  store,
  router,
  i18n,
  render: h => h(App)
}).$mount('#app')
