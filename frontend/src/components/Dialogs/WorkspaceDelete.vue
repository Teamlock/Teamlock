<template>
    <v-dialog
        v-model="open"
        persistent
        max-width="600"
    >
        <v-card>
            <v-card-title class="text-h5">
                {{ $t('label.delete_workspace') }}
            </v-card-title>
            <v-card-text class="text-left">
                {{ $t('warning.alert_delete_workspace') }}
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                    text
                    height="25"
                    small
                    @click="open = false"
                >
                    {{ $t('button.cancel') }}
                </v-btn>
                <v-btn
                    color="primary"
                    text
                    height="25"
                    small
                    @click="deleteWorkspace"
                >
                    {{ $t('button.confirm') }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
    data: () => ({
        open: false,
        workspace_id: null
    }),

    mounted() {
        EventBus.$on("deleteWorkspace", (workspace_id) => {
            this.open = true
            this.workspace_id = workspace_id
        })
    },

    methods: {
         deleteWorkspace() {
            const uri = `/api/v1/workspace/${this.workspace_id}`
            http.delete(uri).then(() => {
                this.open = false
                this.$toast.success(this.$t('success.workspace_deleted'))

                localStorage.removeItem("current_workspace")
                this.$emit("workspaceDeleted")
            })
        },
    }
})
</script>
