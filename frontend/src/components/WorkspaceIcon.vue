<template>
    <v-bottom-navigation :height="50" v-resize-text="{minFontSize: 12}">
        <v-tooltip right>
            <template v-slot:activator="{ on, attrs }">
                <v-btn
                    @click="selectWorkspace"
                    class="workspace-select-button"
                    @contextmenu="showMenu"
                    :loading="workspace.import_in_progress"
                    v-on="on"
                    v-bind="attrs"
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
            </template>
            <span>
                <v-icon small>{{ workspace.icon }}</v-icon>
                {{ workspace.name }}<br>
                <small>{{ $t('help.context_menu_workspace') }}</small>
            </span>
        </v-tooltip>
    </v-bottom-navigation>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import ResizeText from 'vue-resize-text'
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
    components: {},
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
        interval: null
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
                    this.$toast.success("Import successfully ended", {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })
                }
            })
        },

        selectWorkspace() {
            this.loading = true
            this.$emit('selectWorkspace', this.workspace._id, true)
        }
    }
})
</script>
