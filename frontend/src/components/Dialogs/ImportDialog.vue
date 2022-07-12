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
                            <v-file-input
                                @change="inputFileChange('xml')"
                                show-size
                                counter
                                multiple
                                ref="xmlFile"
                                v-model="xml_file"
                                :label="$t('label.xml_file')"
                            />
                        </v-col>
                    </v-row>
                    <v-row dense>
                        <v-col>
                            <v-file-input
                                @change="inputFileChange('backup')"
                                show-size
                                counter
                                multiple
                                ref="teamlockv1_file"
                                v-model="teamlockv1_file"
                                :label="$t('label.teamlockv1_file')"
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
                                :label="$t('label.encrypt_password')"
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
        xml_file: null,
        teamlockv1_file: null,
        form: {
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
        inputFileChange(filetype) {
            if (filetype === "xml") {
                this.teamlockv1_file = null
            } else {
                this.xml_file = null
            }
        },

        importFile() {
            this.loading = true;

            const formData = new FormData()

            if (this.xml_file) {
                formData.append("file", this.xml_file[0])
                formData.append("import_type", "keepass")
            } else {
                formData.append("file", this.teamlockv1_file[0])
                formData.append("import_type", "teamlock_backup")
            }

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
                this.xml_file = null
                this.form = {
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
