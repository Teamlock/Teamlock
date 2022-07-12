<template>
    <v-app id="inspire" :style="renderAppStyle()">
        <app-bar searchBar />

        <v-navigation-drawer ref="drawer" class="drawer-right" app :width="navigation.width" permanent>
            <router-link to="/">
                <small id="version" v-if="version">
                    v{{ version }}
                </small>
                <v-img 
                    v-if="$vuetify.theme.dark"
                    class="mx-auto px-10 logoDark border-bottom-primary"
                    :src="logoWhite"
                    width="100%"
                    height="100"
                    contain
                />
                <v-img v-else
                    class="mx-auto px-10 logo border-bottom-primary"
                    :src="logo"
                    width="100%"
                    height="100"
                    contain
                />
            </router-link>
            <workspace-list />
            <treeview />
        </v-navigation-drawer>

        <add-key />

        <v-main>
            <router-view />
        </v-main>

        <share-dialog />
        <import-dialog />
        <folder-dialog />

  </v-app>
</template>

<script>
import FolderDialog from "../components/Dialogs/FolderDialog.vue"
import ImportDialog from '../components/Dialogs/ImportDialog.vue'
import ShareDialog from '../components/Dialogs/ShareDialog.vue'
import WorkspaceList from '../components/WorkspaceList.vue'
import { defineComponent } from '@vue/composition-api'
import AddKey from '../components/Forms/AddKey.vue'
import KeepAliveMixin from "@/mixins/keepalive"
import Treeview from "../components/Treeview.vue"
import AppBar from '../components/AppBar.vue'
import renderMixin from "@/mixins/render"
import http from "@/utils/http"

export default defineComponent({
    components: {
        WorkspaceList,
        FolderDialog,
        ImportDialog,
        ShareDialog,
        Treeview,
        AddKey,
        AppBar
    },

    mixins: [KeepAliveMixin, renderMixin],

    data: () => ({
        logo: require("@/assets/img/TLAppLogo_Baseline.svg"),
        logoWhite: require("@/assets/img/TLAppLogo_White.svg"),
        rightPanelComponent: null,
        rightPanelOpen: false,
        search: "",
        navigation: {
            borderSize: 2,
            width: 300
        },
        version: null
    }),

    computed: {
        key() {
           return this.$route.path
        }
    },

    beforeMount() {
        const size = localStorage.getItem("treeview_size")
        if (size) {
            this.navigation.width = size
        }

        http.get("/api/v1/version").then((response) => {
            this.version = response.data
        })
    },

    mounted() {
        setTimeout(() => {
            this.setBorderWidth();
            this.setEvents();
        }, 200);
    },

    methods: {
        setBorderWidth() {
            let i = this.$refs.drawer.$el.querySelectorAll(
                ".v-navigation-drawer__border"
            )[1];

            i.style.width = this.navigation.borderSize + "px";
            i.style.cursor = "ew-resize";
        },

        setEvents() {
            const minSize = 300;
            const el = this.$refs.drawer.$el;
            const drawerBorder = el.querySelectorAll(".v-navigation-drawer__border")[1];
            const vm = this;

            const resize = (e) => {
                document.body.style.cursor = "ew-resize";
                let f = e.clientX;
                if (f < minSize) return
                el.style.width = f + "px";
            }

            drawerBorder.addEventListener(
                "mousedown", (e) => {
                if (e.offsetX < minSize) {
                    // let m_pos = e.x;
                    el.style.transition ='initial'; document.addEventListener("mousemove", resize, false);
                }
                },
                false
            );

            document.addEventListener("mouseup", () => {
                    el.style.transition ='';
                    localStorage.setItem("treeview_size", el.style.width)
                    vm.navigation.width = el.style.width;
                    document.body.style.cursor = "";
                    document.removeEventListener("mousemove", resize, false);
                },
                false
            );
        },

        logout() {
            sessionStorage.clear()
            this.$router.push("/login")
        }
  },
})
</script>

<style>
#logo {
    margin: 0 auto;
}
</style>