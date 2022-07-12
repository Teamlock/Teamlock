import Vue from 'vue'
import axios from "axios"
import store from "@/store"
import http from "@/utils/http"
import VueRouter from 'vue-router'
import Auth from "@/views/Auth.vue"
import Layout from "@/layouts/Layout.vue"
import LayoutProfile from "@/layouts/LayoutProfile.vue"
import LayoutAdmin from "@/layouts/LayoutAdmin.vue"

Vue.use(VueRouter)

const ifNotConfigured = (to, from, next) => {
  const url = `/api/v1/user/configure/${to.params.id}`
  http.get(url).then(() => {
    next()
  }).catch((err) => {
    if (err.response.status_code === 404) {
      next("/login")
    }
  })
}

const ifNotInstalled = (to, from, next) => {
  const url = `${process.env.VUE_APP_BASE_URL}/api/v1/config/registration`
  axios.get(url).then(() => {
    next({ name: 'Login' })
  }).catch((err) => {
    if (err.response.status === 418) {
      next()
    }
  })
}

const ifNotAuthenticated = (to, from, next) => {
  const token = sessionStorage.getItem("token")
  if (!token) {
    next()
    return
  }
  next('/')
}

const ifAuthenticated = async (to, from, next) => {
  const token = sessionStorage.getItem("token")
  if (token) {
    const response = await http.get("/api/v1/auth/me")
    const user = response.data

    if (user && user.need_change_password && to.name !== "Profile") {
      next({ name: 'Profile' })
      // } else if (user && !user.recovery_key_downloaded && to.name !== "Profile") {
      //   next({ name: 'Profile' })
    } else {
      next()
    }
  } else {
    sessionStorage.setItem('redirectPath', to.path);
    next({ name: 'Login' })
  }
}

const ifAdmin = async (to, from, next) => {
  let user = store.getters.getUser
  if (!user) {
    const response = await http.get("/api/v1/auth/me")
    user = response.data
  }

  if (user && user.is_admin) {
    next()
    return
  }

  next("/")
}

const routes = [
  {
    path: "/configure/:id",
    component: () => import("@/views/UserConfiguration"),
    name: "User registration",
    beforeEnter: ifNotConfigured
  },
  {
    path: "/register",
    component: () => import("@/views/Register"),
    name: "Registration"
  },
  {
    path: "/recover",
    component: () => import("@/views/Recover"),
    name: "Recover"
  },
  {
    path: "/install",
    component: () => import("@/views/Install"),
    name: "Install",
    beforeEnter: ifNotInstalled
  },
  {
    path: "/",
    component: Layout,
    beforeEnter: ifAuthenticated,
    children: [{
      path: "",
      name: "Home",
      component: () => import("@/views/Home")
    }]
  }, {
    path: "/",
    component: LayoutProfile,
    children: [{
      path: "profile",
      name: "Profile",
      beforeEnter: ifAuthenticated,
      component: () => import("@/views/Profile")
    }, {
      path: "profile/sessions",
      name: "Sessions",
      beforeEnter: ifAuthenticated,
      component: () => import("@/views/Session")
    }]
  }, {
    path: "/admin",
    component: LayoutAdmin,
    children: [{
      path: "",
      name: "Admin",
      beforeEnter: ifAdmin,
      component: () => import("@/views/admin/Admin")
    }, {
      path: "users",
      name: "Users",
      beforeEnter: ifAdmin,
      component: () => import("@/views/admin/Users")
    }, {
      path: "history",
      name: "History",
      beforeEnter: ifAdmin,
      component: () => import("@/views/admin/History")
    }]
  },
  {
    path: '/login',
    name: 'Login',
    component: Auth,
    beforeEnter: ifNotAuthenticated,
  },
]

const router = new VueRouter({
  // mode: 'history',
  // base: process.env.BASE_URL,
  routes
})

export default router
