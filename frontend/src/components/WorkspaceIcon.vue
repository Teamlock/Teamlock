<template>
    <v-bottom-navigation :height="50" v-resize-text="{minFontSize: 12}">
        <v-btn
            @click="selectWorkspace"
            class="workspace-select-button"
            @contextmenu.native="openContextMenu"
            :loading="workspace.import_in_progress"
            :color="color"
            :height="50"
            :width="60"
            block
            small
            tile
        >
            <small class="workspace-icon-name">{{ workspace.name }}</small>
            <v-icon class="workspace-icon">{{ workspace.icon }}</v-icon>
        </v-btn>
        <v-menu
            :position-x="x"
            :position-y="y"
            offset-y
            v-model="contextMenuOpen"
        >
            <context-workspace :workspace="workspace" />
        </v-menu>
    </v-bottom-navigation>
</template>

<script>
import ContextWorkspace from './Context/ContextWorkspace.vue'
import { defineComponent } from '@vue/composition-api'
import 'vue-context/src/sass/vue-context.scss';
import ResizeText from 'vue-resize-text'
import VueContext from 'vue-context';
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
    components: {
        ContextWorkspace,
        VueContext
    },
    directives: {
        ResizeText
    },

    props: {
        selected: {
            type: Boolean,
            default: false
        },

        owner: {
            type: Boolean,
            default: false
        },

        workspace: {
            type: Object,
            required: true
        }
    },

    data: () => ({
        x: 0,
        y: 0,
        interval: null,
        loading: false,
        contextMenuOpen: false
    }),

    computed: {
        color() {
            return this.selected ? "secondary" : "";
        }
    },

    destroyed() {
        if (this.interval) {
            clearInterval(this.interval)
        }
    },

    mounted() {
        if (this.workspace.import_in_progress) {
            this.startInterval()
        }
    },

    methods: {
        showMenu(e) {
            this.$emit('showMenu', e, this.workspace)
        },

        startInterval() {
            this.interval = setInterval(() => {
                this.fetchWorkspace()
            }, 5000)
        },

        fetchWorkspace() {
            const uri = `/api/v1/workspace/${this.workspace._id}`
            http.get(uri).then((response) => {
                if (!response.data.import_in_progress) {
                    EventBus.$emit("importFinished", this.workspace._id)
                    clearInterval(this.interval)
                    this.$toast.success("Import successfully ended")
                    this.loading = false;
                }
            })
        },

        selectWorkspace() {
            this.loading = true
            this.$emit('selectWorkspace', this.workspace._id, true)
        },

        openContextMenu(e) {
            e.preventDefault()
            e.stopPropagation()
            this.x = e.clientX
            this.y = e.clientY
            this.$nextTick(() => {
                this.contextMenuOpen = true
            })
        }
    }
})
</script>
