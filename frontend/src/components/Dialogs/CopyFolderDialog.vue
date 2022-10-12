<template>
    <v-dialog
        :max-width="400"
        v-model="open"
        persistent
    >
        <v-card :loading="is_loading">
            <v-card-title class="text-h5">
                {{ $t('folder.copy') }}
            </v-card-title>
            <v-card-text>
                <p>{{ $t('folder.confirm_copy') }}</p>
                <v-select
                    :label="$t('label.target_workspace')"
                    :items="workspaces_list"
                    v-model="to_workspace"
                    item-text="name"
                    item-value="id"
                />
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                    text
                    small
                    @click="open = false"
                >
                    {{ $t('button.cancel') }}
                </v-btn>
                <v-btn
                    @click="copyFolder"
                    :loading="is_loading"
                    color="primary"
                    text
                    small
                >
                    {{ $t('button.confirm') }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import http from "@/utils/http"

export default defineComponent({
    props: {
        folder_id: {
            type: String,
            required: false
        }
    },

    data: () => ({
        workspaces_list: [],
        to_workspace: null,
        is_loading: false,
        open: false,
    }),

    watch: {
        folder_id() {
            this.fetchWorkspaces()
        }
    },

    methods: {
        async fetchWorkspaces() {
            this.workspaces_list = []
            const response = await http.get("/api/v1/workspace/")
            for (const tmp of response.data) {
                if (tmp._id !== this.$store.state.selected_workspace._id) {
                    this.workspaces_list.push({
                        id: tmp._id,
                        name: tmp.name
                    })
                }
            }
        },

        copyFolder() {
             if (!this.to_workspace) return
            
            this.is_loading = true;
            const uri = `/api/v1/folder/${this.folder_id}/copy`
            http.post(uri, this.to_workspace).then(() => {
                this.$toast.success(this.$t("success.folder_copied"))

                this.is_loading = false
                this.open = false
                this.to_workspace = null
                this.$emit("folderDeleted")
            })
        },
    }
})
</script>
