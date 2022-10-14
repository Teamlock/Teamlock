<template>
    <v-app id="inspire" :style="renderAppStyle()">
        <app-bar searchBar />

        <v-navigation-drawer ref="drawer" class="drawer-right" app :width="navigation.width" permanent>
            
            <router-link to="/">
                <v-img 
                    :class="logoClass"
                    :src="logo"
                    width="100%"
                    height="100"
                    contain
                />
            </router-link>
            <workspace-list />
            <treeview />
 
            <v-btn class="trash" @click="showTrash" :color="activeTrash">
                <v-icon>mdi-delete</v-icon>
                {{ $t('label.trash') }}
            </v-btn>
        </v-navigation-drawer>

        <add-login />
        <add-server />
        <add-phone />
        <add-bank />

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
import AddLogin from '../components/Forms/AddLogin.vue'
import AddPhone from '../components/Forms/AddPhone.vue'
import AddServer from '../components/Forms/AddServer.vue'
import { defineComponent } from '@vue/composition-api'
import AddBank from "../components/Forms/AddBank.vue"
import KeepAliveMixin from "@/mixins/keepalive"
import Treeview from "../components/Treeview.vue"
import AppBar from '../components/AppBar.vue'
import designMixin from "@/mixins/design"
import renderMixin from "@/mixins/render"
import EventBus from "@/event"

export default defineComponent({
    components: {
        WorkspaceList,
        FolderDialog,
        ImportDialog,
        ShareDialog,
        Treeview,
        AddServer,
        AddLogin,
        AddPhone,
        AppBar,
        AddBank
    },

    mixins: [KeepAliveMixin, renderMixin, designMixin],

    data: () => ({
        rightPanelComponent: null,
        rightPanelOpen: false,
        trashShowed: false,
        search: "",
        navigation: {
            borderSize: 2,
            width: 300
        },
    }),

    computed: {
        key() {
           return this.$route.path
        },

        activeTrash() {
            return this.trashShowed ? "primary" : "dark"
        }
    },

    beforeMount() {
        const size = localStorage.getItem("treeview_size")
        if (size) {
            this.navigation.width = size
        }
    },

    mounted() {
        this.trashShowed = localStorage.getItem("showTrash") === "true"
        setTimeout(() => {
            this.setBorderWidth();
            this.setEvents();
        }, 200);

        EventBus.$on("showTrash", (val) => {
            this.trashShowed = val
        })
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
        },

        showTrash(){
            EventBus.$emit("showTrash", true)
            localStorage.setItem("showTrash", true)
        }
  },
})
</script>

<style>
#logo {
    margin: 0 auto;
}
</style>