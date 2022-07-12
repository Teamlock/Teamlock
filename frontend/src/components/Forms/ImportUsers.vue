<template>
    <v-card>
        <v-form ref="form" @submit.prevent="importUsers">
            <v-app-bar flat dense class="edit_workspace_bar">
                <v-app-bar-nav-icon>
                    <v-icon>mdi-account-group</v-icon>
                </v-app-bar-nav-icon>
                <v-toolbar-title class="pl-0">
                    {{ $t("title.import_users") }}
                </v-toolbar-title>
            </v-app-bar>

            <v-card-text>
                <v-row dense>
                    <v-col>
                        <v-alert type="success" border="top" class="mt-4">
                            {{ $t("help.import_users") }}
                        </v-alert>
                    </v-col>
                </v-row>

                <v-row dense v-if="Object.keys(email_addresses).length === 0">
                    <v-col>
                        <v-file-input v-model="file" ref="file" :label="$t('label.csv_file')"/>
                    </v-col>
                </v-row>

                <v-row v-else>
                    <v-list>
                        <v-subheader>{{ $t("label.users_to_import")}}:</v-subheader>
                        <v-list-item v-for="(err, email) in email_addresses" :key="email">
                            <v-list-item-content>
                                <v-list-item-title>{{ email }}</v-list-item-title>
                            </v-list-item-content>
                            <v-list-item-icon v-if="err">
                                <span v-if="err === 'EXISTS'">
                                    <v-tooltip bottom color="error">
                                        <template v-slot:activator="{ on, attrs }">
                                            <v-icon v-bind="attrs" v-on="on">mdi-close-thick</v-icon>
                                        </template>
                                        <span>{{ $t("error.unique_user")}}</span>
                                    </v-tooltip>
                                </span>
                                <v-icon v-else>mdi-check</v-icon>
                            </v-list-item-icon>
                        </v-list-item>
                    </v-list>
                </v-row>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>

                <v-btn
                    text
                    x-small
                    @click="close"
                >
                    {{ $t("button.close") }}
                </v-btn>
                <v-btn
                    v-if="Object.keys(email_addresses).length === 0"
                    color="primary"
                    type="button"
                    @click="loadFile"
                    x-small
                    text
                    :loading="is_loading"
                >
                    {{ $t("button.load") }}
                </v-btn>
                <v-btn
                    v-if="Object.keys(email_addresses).length > 0 && !imported"
                    color="primary"
                    type="submit"
                    x-small
                    text
                    :loading="is_loading"
                >
                    {{ $t("button.import") }}
                </v-btn>
            </v-card-actions>
        </v-form>
    </v-card>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import http from "@/utils/http";

export default defineComponent({
    data: () => ({
        is_loading: false,
        email_addresses: {},
        imported: false,
        file: null
    }),

    methods: {
        close() {
            this.email_addresses = {}
            this.imported = false
            this.file = null
            this.$emit('close')
        },

        loadFile() {
            const reader = new FileReader();
            reader.onload = (e) => {
                const res = e.target.result
                for (const tmp of res.split("\n")) {
                    this.email_addresses[tmp] = false
                }

                this.$forceUpdate()
            }

            reader.readAsText(this.file)
        },

        importUsers() {
            this.is_loading = true

            const form = []
            for (const email of Object.keys(this.email_addresses)) {
                form.push({
                    email: email
                })
            }

            http.post("/api/v1/user/bulk", form).then((response) => {
                for (const error of response.data.errors) {
                    this.email_addresses[error.email] = error.error
                }

                for (const success of response.data.success) {
                    this.email_addresses[success] = true
                }

                this.imported = true
                this.$toast.success(this.$t("success.users_created"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
            }).catch((error) => {
                if (error.response.data.detail === "MAX USERS LIMIT") {
                    this.$toast.error(this.$t("error.max_users_limit"), {
                        closeOnClick: true,
                        timeout: 5000,
                        icon: true
                    })
                } else {
                    this.$toast.error(this.$t("error.unknown"), {
                        closeOnClick: true,
                        timeout: 5000,
                        icon: true
                    })
                }
            }).then(() => {
                this.is_loading = false
            })
        }
    }
})
</script>
