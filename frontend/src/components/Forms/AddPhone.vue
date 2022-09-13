<template>
    <v-navigation-drawer app temporary hide-overlay right v-model="open" width="500px">
        <v-form ref="form" @submit.prevent="savePhone" style="height: 100%">
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
                        >
                            <v-tooltip bottom slot="append">
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon
                                        v-on="on"
                                        v-bind="attrs"
                                        :color="form.name.encrypted ? '#daab39' : ''"
                                        v-html="form.name.encrypted ? 'mdi-lock' : 'mdi-lock-open'"
                                        @click="form.name.encrypted = !form.name.encrypted"
                                        tabindex="-1"
                                    />
                                </template>
                                <span v-html="$t('label.encrypt')" />
                            </v-tooltip>
                        </v-text-field>
                    </v-row>
                    <v-row dense class="relative-row">
                        <v-text-field
                            color="#DAAB39"
                            v-model="form.number.value"
                            class="input-field pl-1 pr-1 mb-2"
                            :label="$t('label.number')"
                            hide-details
                            required
                        >
                            <v-tooltip bottom slot="append">
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon
                                        v-on="on"
                                        v-bind="attrs"
                                        :color="form.number.encrypted ? '#daab39' : ''"
                                        v-html="form.number.encrypted ? 'mdi-lock' : 'mdi-lock-open'"
                                        @click="form.number.encrypted = !form.number.encrypted"
                                        tabindex="-1"
                                    />
                                </template>
                                <span v-html="$t('label.encrypt')" />
                            </v-tooltip>
                        </v-text-field>
                    </v-row>
                    <v-row dense class="relative-row">
                        <v-text-field
                            class="input-field pl-1 pr-1 mb-0"
                            v-model="form.pin_code.value"
                            :type="show_pin_code ? 'text' : 'password'"
                            :label="$t('label.pin_code')"
                            hide-details
                        >
                            <span slot="append">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            v-html="show_pin_code ? 'mdi-eye' : 'mdi-eye-off'"
                                            @click="show_pin_code = !show_pin_code"
                                            tabindex="-1"
                                        />                                    
                                    </template>
                                    <span v-html="$t('label.show_pin')" />
                                </v-tooltip>
                            </span>
                        </v-text-field>
                    </v-row>
                    <v-row dense class="relative-row">
                        <v-text-field
                            class="input-field pl-1 pr-1 mb-2"
                            v-model="form.puk_code.value"
                            :type="show_puk_code ? 'text' : 'password'"
                            :label="$t('label.puk_code')"
                            hide-details
                        >
                            <span slot="append">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            v-html="show_puk_code ? 'mdi-eye' : 'mdi-eye-off'"
                                            @click="show_puk_code = !show_puk_code"
                                            tabindex="-1"
                                        />                                    
                                    </template>
                                    <span v-html="$t('label.show_pin')" />
                                </v-tooltip>
                            </span>
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
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
    name: "AddPhone",
    data: () => ({
        open: false ,
        secret_id: null,
        show_pin_code: false,
        show_puk_code: false,
        loading: false,
        show: ["pin_code", "puk_code"],
        errors: [],
        form: {
            secret_type: "phone",
            name: {encrypted: false, value: ""},
            number: {encrypted: false, value: ""},
            pin_code: {encrypted: true, value: ""},
            puk_code: {encrypted: true, value: ""},
            informations: {encrypted: false, value: ""}
        }
    }),

    computed: {
        title() {
            return this.secret_id ? this.$t('title.edit_phone') : this.$t("title.add_phone")
        }
    },

    watch: {
        open(val) {
            if (!val) {
                this.form = {
                    secret_type: "phone",
                    name: {encrypted: false, value: ""},
                    number: {encrypted: false, value: ""},
                    pin_code: {encrypted: true, value: ""},
                    puk_code: {encrypted: true, value: ""},
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
        EventBus.$on("edit_phone", (secret_id, folder_id) => {
            for (const input of this.show) {
                this[`show_${input}`] = secret_id === null
            }

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

                this.form = {
                    secret_type: 'phone',
                    name: secret.name,
                    number: secret.number,
                    pin_code: secret.pin_code,
                    puk_code: secret.puk_code,
                    informations: secret.informations
                }
            }).then(() => {
                this.loading = false
            })
        },

        closePanel() {
            this.form = {
                secret_type: 'phone',
                name: "",
                number: "",
                pin_code: "",
                puk_code: "",
                informations: ""
            }
            this.show_pin_code = false
            this.show_puk_code = false
            this.open = false
        },

        async savePhone() {
            this.loading = true;
            let uri = "/api/v1/secret/"
            let message = "success.secret_created"
            const secret_id = this.secret_id
            this.form.folder = this.folder_id

            if (secret_id) {
                uri += secret_id
                await http.put(uri, {secret: this.form})
                message = "success.secret_updated"
            } else {
                await http.post(uri, {secret: this.form})
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
