import Vue from "vue"
import Vuex from "vuex"
import router from "../router"
import http from "@/utils/http"
import EventBus from "@/event"

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        pro: false,
        user: null,
        twilio: false,
        current_folder: null,
        selected_workspace: null,
        totp_enforce: false,
    },

    getters: {
        getWorkspace: state => state.selected_workspace,
        getFolder: state => state.current_folder,
        getTwilio: state => state.twilio,
        getUser: state => state.user,
        getPro: state => state.pro,
        getNeedConfigureOtp : state => state.user?.otp?.need_configure,
        getTotpEnforce : state => state.totp_enforce
    },

    mutations: {
        SET_PRO(state, value) {
            state.pro = value
        },

        SET_TWILIO(state, value) {
            state.twilio = value
        },

        SET_USER(state, user) {
            state.user = user
        },

        SET_CURRENT_FOLDER(state, folder) {
            state.current_folder = folder
            EventBus.$emit("refreshSecrets")
        },

        async REFRESH_USER(state) {
            const response = await http.get("/api/v1/auth/me")
            state.user = response.data
        },

        async SET_WORKSPACE(state, workspace_id) {
            if (workspace_id) {
                sessionStorage.setItem("current_workspace", workspace_id)
                const response = await http.get(`/api/v1/workspace/${workspace_id}`)
                state.selected_workspace = response.data
                EventBus.$emit("refreshTreeview")
                EventBus.$emit("workspaceSelected")
            } else {
                state.selected_workspace = null
            }
        },

        SET_TOTP_ENFORCE(state, value) {
            state.totp_enforce = value
        },
    },

    actions: {
        reload_user({ commit }) {
            commit("REFRESH_USER")
        },

        async set_user({ commit }) {
            const response = await http.get("/api/v1/auth/me")
            if (response.status !== 200) {
                sessionStorage.clear()
                router.push({ name: "Login" })
                return
            }

            const user = response.data
            commit("SET_USER", user)
            if (user.need_change_password) {
                router.push({ name: "Profile" })
            }
        },

        set_current_folder({ commit }, folder_id) {
            commit("SET_CURRENT_FOLDER", folder_id)
        },

        change_workspace({ commit }, workspace_id) {
            commit("SET_WORKSPACE", workspace_id)
            commit("SET_CURRENT_FOLDER", null)
        },

        async set_twilio({ commit }) {
            const response = await http.get("/api/v1/config/twilio")
            commit("SET_TWILIO", response.data)
        },

        async set_pro({ commit }) {
            try {
                await http.get("/pro/")
                commit("SET_PRO", true)
            } catch {
                console.log("NO PRO")
            }
        },

        async set_enforce_totp({commit, state}){
            if (!state.pro) commit("SET_TOTP_ENFORCE", false);
            else{
                const response = await http.get("/pro/api/v1/config");
                if (response.status === 200) {
                    commit("SET_TOTP_ENFORCE", response.data.enforce_totp);
                }else commit("SET_TOTP_ENFORCE", false);
            }
        }
    }
})
