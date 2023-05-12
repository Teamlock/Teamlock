<template>
    <v-dialog
        v-model="open"
        persistent
        max-width="600"
    >
        <v-card>
            <v-card-title class="text-h5">
                {{ $t('label.export_workspace') }}
            </v-card-title>
            <v-card-text class="text-left">
                <v-text-field
                    type="password"
                    v-model="password"
                    :hint="$t('help.export_workspace_password')"
                    persistent-hint
                    :label="$t('label.password')"
                />
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
                    :loading="isLoading"
                    @click="exportWorkspace"
                >
                    {{ $t('button.confirm') }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import http from "@/utils/http"
import EventBus from "@/event"

export default {
    data: () => ({
        isLoading: false,
        workspace: "",
        open: false,
        password: ""
    }),

    mounted() {
        EventBus.$on("exportWorkspace", (workspace) => {
            this.workspace = workspace
            this.open = true
        })
    },

    methods: {
        exportWorkspace() {
            if (!this.password) {
                return
            }

            const data = {
                password: this.password
            }

            this.isLoading = true
            http.post(`/api/v1/workspace/${this.workspace._id}/export`, data, {
                responseType: 'blob'
            })
                .then((response) => {
                    console.log(response)
                    const fileURL = window.URL.createObjectURL(new Blob([response.data]));
                    const fileLink = document.createElement('a');
                    fileLink.href = fileURL;
                    fileLink.setAttribute('download', `${this.workspace.name}.kdbx`);
                    document.body.appendChild(fileLink);
                    fileLink.click();
                    this.password = ""
                    this.workspace = ""
                    this.open = false
                })
                .then(() => {
                    this.isLoading = false
                })
        }
    }
}
</script>
