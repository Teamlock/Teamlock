<template>
    <v-dialog v-model="open" width="600" scrollable>
        <v-card v-if="open">
            <v-form ref="form" @submit.prevent="importFile">
                <v-app-bar flat dense>
                    <v-app-bar-nav-icon v-if="selected_workspace.icon">
                        <v-icon>mdi-upload</v-icon>
                    </v-app-bar-nav-icon>
                    <v-toolbar-title class="pl-0">
                        {{ $t('label.import_workspace') }}
                    </v-toolbar-title>
                </v-app-bar>

                <v-card-text>
                    <v-row dense>
                        <v-alert style="width: 100%" dense color="primary" border-top>{{ $t('warning.import') }}</v-alert>
                    </v-row>
                    <v-row dense>
                        <v-col>
                            <v-select
                                :items="importChoices"
                                :label="$t('label.import_type')"
                                v-model="form.import_type"
                                item-value="value"
                                item-text="text"
                            />
                        </v-col>
                    </v-row>
                    <v-row dense>
                        <v-col>
                            <v-file-input
                                show-size
                                counter
                                ref="file"
                                v-model="file"
                                :label="$t('label.file')"
                            />
                        </v-col>
                    </v-row>

                    <v-row dense>
                        <v-col>
                            <v-switch
                                v-model="form.encrypt_name"
                                :label="$t('label.encrypt_name')"
                            />
                            <v-switch
                                v-model="form.encrypt_url"
                                :label="$t('label.encrypt_url')"
                            />
                            <v-switch
                                v-model="form.encrypt_informations"
                                :label="$t('label.encrypt_informations')"
                            />
                        </v-col>
                        <v-col>
                            <v-switch
                                v-model="form.encrypt_login"
                                :label="$t('label.encrypt_login')"
                            />
                            <v-switch
                                v-model="form.encrypt_password"
                                :label="$t('label.encrypt_secret')"
                                disabled
                            />
                        </v-col>
                    </v-row>
                </v-card-text>
                <v-card-actions>
                    <v-spacer />
                    <v-btn text  small @click="open = false">{{ $t('button.cancel') }}</v-btn>
                    <v-btn color="primary"  small text type="submit" :loading="loading">{{ $t('button.submit') }}</v-btn>
                </v-card-actions>
            </v-form>
        </v-card>
    </v-dialog>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import { mapGetters } from 'vuex'
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
    data: () => ({
        loading: false,
        open: false,
        file: null,
        importChoices: [
            {value: 'keepass', text: 'KeePass XML File'},
            {value: 'teamlock_v1', text: 'Teamlock v1'},
            {value: 'bitwarden', text: 'Bitwarden JSON'}
        ],
        form: {
            import_type: null,
            encrypt_name: false,
            encrypt_url: false,
            encrypt_login: false,
            encrypt_password: true,
            encrypt_informations: false
        }
    }),

    computed: {
        ...mapGetters({
            selected_workspace: 'getWorkspace'
        }),
    },

    mounted() {
        EventBus.$on("importXML", () => {
            this.open = true;
        })
    },

    methods: {
        importFile() {
            this.loading = true;

            const formData = new FormData()
            formData.append("file", this.file)
            formData.append("import_type", this.form.import_type)
            formData.append("encrypt_name", this.form.encrypt_name)
            formData.append("encrypt_url", this.form.encrypt_url)
            formData.append("encrypt_login", this.form.encrypt_login)
            formData.append("encrypt_password", this.form.encrypt_password)
            formData.append("encrypt_informations", this.form.encrypt_informations)

            http.post(`/api/v1/workspace/${this.selected_workspace._id}/import`, formData, {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            }).then(() => {
                this.loading = false
                this.file = null
                this.form = {
                    import_type: null,
                    encrypt_name: false,
                    encrypt_url: false,
                    encrypt_login: false,
                    encrypt_password: true,
                    encrypt_informations: false
                }

                this.$toast.success(this.$t('success.import_running'), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })

                setTimeout(() => {
                    this.open = false
                    EventBus.$emit("reloadWorkspaces")
                }, 200)
            }).catch((error) => {
                this.loading = false
                throw error
            })
        }
    }
})
</script>
