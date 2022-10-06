<template>
    <v-navigation-drawer app temporary hide-overlay right v-model="open" width="500px">
        <v-form ref="form" @submit.prevent="saveLogin" style="height: 100%">
            <v-card :loading="loading" class="mx-auto" :min-width="400" flat style="height: 100%">
                <v-app-bar flat dense class="edit_workspace_bar">
                    <v-app-bar-nav-icon>
                        <v-icon>mdi-key-plus</v-icon>
                    </v-app-bar-nav-icon>
                    <v-toolbar-title class="pl-0" v-html="title"/>
                </v-app-bar>
                <v-card-text>
                    <v-row dense>
                        <v-col>
                            <v-alert
                                border="top"
                                color="#daab39"
                            >
                                <v-icon color="#daab39">mdi-alert-circle-outline</v-icon>
                                {{ $t('warning.key_encryption') }}
                            </v-alert>
                        </v-col>
                    </v-row>
                    <v-row dense class="relative-row">
                        <v-text-field
                            v-model="form.name.value"
                            color="#DAAB39"
                            class="input-field pl-1 pr-1 mb-2"
                            :label="$t('label.name')"
                            ref="name_input"
                            hide-details
                            required
                            suffix
                        />
                    </v-row>
                    <v-row dense class="relative-row">
                        <v-text-field
                            color="#DAAB39"
                            v-model="form.login.value"
                            class="input-field pl-1 pr-1 mb-2"
                            :label="$t('label.login')"
                            hide-details
                            required
                        >
                            <v-tooltip bottom slot="append">
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon
                                        v-on="on"
                                        v-bind="attrs"
                                        :color="form.login.encrypted ? '#daab39' : ''"
                                        v-html="form.login.encrypted ? 'mdi-lock' : 'mdi-lock-open'"
                                        @click="form.login.encrypted = !form.login.encrypted"
                                        tabindex="-1"
                                    />
                                </template>
                                <span v-html="$t('label.encrypt')" />
                            </v-tooltip>
                        </v-text-field>
                    </v-row>
                    <v-row
                        v-for="(value, index) of form.urls.value"
                        :key="index"
                        dense
                        class="relative-row"
                    >
                        <v-text-field
                            color="#DAAB39"
                            v-model="form.urls.value[index]"
                            class="input-field pl-1 pr-1 mb-2"
                            :label="$t('label.url')"
                            hide-details
                            required
                        >
                            <span slot="prepend">
                                <v-tooltip v-if="index === form.urls.value.length -1" bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            @click="form.urls.value.push('')"
                                            tabindex="-1"
                                        >
                                            mdi-plus
                                        </v-icon>
                                    </template>
                                    <span v-html="$t('label.add')" />
                                </v-tooltip>
                            </span>
                            <span slot="append">
                                <v-tooltip v-if="index > 0" bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            @click="form.urls.value.splice(index, 1)"
                                            tabindex="-1"
                                            style="float: left"
                                        >
                                            mdi-close
                                        </v-icon>
                                    </template>
                                    <span v-html="$t('label.remove')" />
                                </v-tooltip>
                                <v-tooltip v-if="index === 0" bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            :color="form.urls.encrypted ? '#daab39' : ''"
                                            v-html="form.urls.encrypted ? 'mdi-lock' : 'mdi-lock-open'"
                                            @click="form.urls.encrypted = !form.urls.encrypted"
                                            tabindex="-1"
                                        />
                                    </template>
                                    <span v-html="$t('label.encrypt')" />
                                </v-tooltip>
                            </span>
                        </v-text-field>
                    </v-row>
                    <v-row dense class="relative-row">
                        <v-text-field
                            class="input-field pl-1 pr-1 mb-2"
                            v-model="form.password.value"
                            :type="show_password ? 'text' : 'password'"
                            :error-messages="errorPassword"
                            :error-count="errorPasswordCount"
                            :hide-details="errorPasswordCount === 0"
                            :label="$t('label.password')"
                        >
                            <span slot="prepend">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            @click="generatePassword"
                                            class="mr-2"
                                            tabindex="-1"
                                        >
                                            mdi-auto-fix
                                        </v-icon>
                                    </template>
                                    <span v-html="$t('label.generate_password')" />
                                </v-tooltip>
                            </span>
                            <span slot="append">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            v-html="show_password ? 'mdi-eye' : 'mdi-eye-off'"
                                            @click="show_password = !show_password"
                                            tabindex="-1"
                                        />                                    
                                    </template>
                                    <span v-html="$t('label.show_password')" />
                                </v-tooltip>
                            </span>
                        </v-text-field>
                    </v-row>
                    <v-row dense class="relative-row">
                        <v-text-field
                            color="#DAAB39"
                            v-model="form.ip.value"
                            :label="$t('label.ip')"
                            class="input-field pl-1 pr-1 mb-2"
                            type="text"
                            hide-details
                        >
                            <v-tooltip bottom slot="append">
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon
                                        v-on="on"
                                        v-bind="attrs"
                                        :color="form.ip.encrypted ? '#daab39' : ''"
                                        v-html="form.ip.encrypted ? 'mdi-lock' : 'mdi-lock-open'"
                                        @click="form.ip.encrypted = !form.ip.encrypted"
                                        tabindex="-1"
                                    />
                                </template>
                                <span v-html="$t('label.encrypt')" />
                            </v-tooltip>
                        </v-text-field>
                    </v-row>
                    <v-row dense class="relative-row">
                        <v-textarea
                            filled
                            color="#daab39"
                            class="mt-2 pl-1 pr-1 mb-10"
                            height="200"
                            hide-details
                            :label="$t('label.informations')"
                            v-model="form.informations.value"
                        >
                            <v-tooltip bottom slot="append">
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon
                                        v-on="on"
                                        v-bind="attrs"
                                        :color="form.informations.encrypted ? '#daab39' : ''"
                                        v-html="form.informations.encrypted ? 'mdi-lock' : 'mdi-lock-open'"
                                        @click="form.informations.encrypted = !form.informations.encrypted"
                                        tabindex="-1"
                                    />
                                </template>
                                <span v-html="$t('label.encrypt')" />
                            </v-tooltip>
                        </v-textarea>
                    </v-row>
                </v-card-text>

                <v-card-actions class="card-actions">
                    <v-spacer></v-spacer>
                    <v-btn small text @click="closePanel">{{ $t("button.cancel") }}</v-btn>
                    <v-btn small color="primary" text type="submit">{{ $t("button.submit") }}</v-btn>
                </v-card-actions>
            </v-card>
        </v-form>
    </v-navigation-drawer>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import http from "@/utils/http"
import EventBus from "@/event"

export default defineComponent({
    name: "AddLogin",
    data: () => ({
        open: false ,
        secret_id: null,
        show_password: false,
        loading: false,
        errorPassword: [],
        errorPasswordCount: 0,
        errors: [],
        form: {
            secret_type: "login",
            name: {encrypted: false, value: ""},
            urls: {encrypted: false, value: [""]},
            login: {encrypted: false, value: ""},
            password: {encrypted: true, value: ""},
            ip: {encrypted: false, value: ""},
            informations: {encrypted: false, value: ""}
        }
    }),

    computed: {
        title() {
            return this.secret_id ? this.$t('title.edit_login') : this.$t("title.add_login")
        }
    },

    watch: {
        open(val) {
            if (!val) {
                this.form = {
                    secret_type: "login",
                    name: {encrypted: false, value: ""},
                    urls: {encrypted: false, value: [""]},
                    login: {encrypted: false, value: ""},
                    password: {encrypted: true, value: ""},
                    ip: {encrypted: false, value: ""},
                    informations: {encrypted: false, value: ""}
                }
            } else {
                setTimeout(() => {
                    this.$refs.name_input.focus()
                }, 200);
            }
        }
    },

    mounted() {
        EventBus.$on("edit_login", (secret_id, folder_id) => {
            this.secret_id = secret_id
            this.folder_id = folder_id
            this.open = true

            if (this.secret_id) {
                this.getSecret()
            }
        })
    },

    methods: {
        getSecret() {
            this.loading = true
            const uri =  `/api/v1/secret/${this.secret_id}`

            http.get(uri).then((response) => {
                const secret = response.data
                this.folder_id = secret.folder

                if (secret.urls.value.length === 0) {
                    secret.urls.value = [""]
                }

                this.form = {
                    secret_type: 'login',
                    name: secret.name,
                    login: secret.login,
                    password: secret.password,
                    urls: secret.urls,
                    ip: secret.ip,
                    informations: secret.informations
                }
            }).then(() => {
                this.loading = false
            })
        },

        closePanel() {
            this.form = {
                secret_type: 'login',
                name: "",
                urls: {value: [""]},
                login: "",
                password: "",
                ip: "",
                informations: ""
            }
            this.show_password = false
            this.errorPassword = []
            this.errorPasswordCount = 0
            this.open = false
        },

        generatePassword() {
            this.loading = true

            const params = {
                folder_id: this.folder_id
            }

            http.get("/api/v1/secret/generate", { params: params })
                .then((response) => {
                    this.form.password.value = response.data
                })
                .then(() => {
                    this.loading = false
                })
        },

        hasErrors(error) {
            const mapping = {
                length: this.$t("label.password_length"),
                uppercase: this.$t("label.password_upper"),
                numbers: this.$t("label.password_number"),
                special: this.$t("label.password_special")
            }

            if (!error.response) {
                return false
            }

            if (error.response.status === 400) {
                let detail = [error.response.data.detail.error]
                for (const {type, min} of error.response.data.detail.details) {
                    detail.push(`${mapping[type]}: ${min}`)
                }

                this.errorPassword = detail
                this.errorPasswordCount = detail.length + 1
            } else {
                this.$toast.error(this.$t("error.occurred"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
                this.loading = false
                throw error
            }

            return this.errorPasswordCount > 0
        },

        async saveLogin() {
            this.errorPassword = []
            this.loading = true;
            let uri = "/api/v1/secret/"
            let message = "success.secret_created"
            const secret_id = this.secret_id
            this.form.folder = this.folder_id

            if (secret_id) {
                uri += secret_id
                try {
                    await http.put(uri, {secret: this.form})
                    message = "success.secret_updated"
                } catch (error){
                    if (this.hasErrors(error)) {
                        this.loading = false;
                        return
                    }
                }
            } else {
                try {
                    await http.post(uri, {secret: this.form})
                } catch(error) {
                    if (this.hasErrors(error)) {
                        this.loading = false;
                        return
                    }
                }
            }

            EventBus.$emit("refreshSecrets")
            EventBus.$emit("refreshStats")
            this.loading = false;
            this.$toast.success(this.$t(message), {
                closeOnClick: true,
                timeout: 3000,
                icon: true
            })
            this.closePanel()
        }
    }
})
</script>


<style scoped>
    @font-face {
        font-family: "Coolvetica";
        src: url("../../assets/fonts/coolvetica condensed rg.otf") format("woff2"),
    }

    .input-field >>> input{
        padding-left: 5px;
    }
</style>
