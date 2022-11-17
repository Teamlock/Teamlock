<template>
    <v-navigation-drawer app temporary hide-overlay right v-model="open" width="500px">
        <v-form ref="form" @submit.prevent="saveBank" style="height: 100%">
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
                            v-model="form.owner.value"
                            class="input-field pl-1 pr-1 mb-2"
                            :label="$t('label.owner')"
                            hide-details
                            required
                        >
                            <v-tooltip bottom slot="append">
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon
                                        v-on="on"
                                        v-bind="attrs"
                                        :color="form.owner.encrypted ? '#daab39' : ''"
                                        v-html="form.owner.encrypted ? 'mdi-lock' : 'mdi-lock-open'"
                                        @click="form.owner.encrypted = !form.owner.encrypted"
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
                            v-model="form.bank_name.value"
                            class="input-field pl-1 pr-1 mb-2"
                            :label="$t('label.bank_name')"
                            hide-details
                            required
                        >
                            <v-tooltip bottom slot="append">
                                <template v-slot:activator="{ on, attrs }">
                                    <v-icon
                                        v-on="on"
                                        v-bind="attrs"
                                        :color="form.bank_name.encrypted ? '#daab39' : ''"
                                        v-html="form.bank_name.encrypted ? 'mdi-lock' : 'mdi-lock-open'"
                                        @click="form.bank_name.encrypted = !form.bank_name.encrypted"
                                        tabindex="-1"
                                    />
                                </template>
                                <span v-html="$t('label.encrypt')" />
                            </v-tooltip>
                        </v-text-field>
                    </v-row>
                    <v-row dense class="relative-row">
                        <v-text-field
                            class="input-field pl-1 pr-1 mb-2"
                            v-model="form.iban.value"
                            :type="show_iban ? 'text' : 'password'"
                            :label="$t('label.iban')"
                            hide-details
                        >
                            <span slot="append">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            v-html="show_iban ? 'mdi-eye' : 'mdi-eye-off'"
                                            @click="show_iban = !show_iban"
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
                            v-model="form.bic.value"
                            :type="show_bic ? 'text' : 'password'"
                            :label="$t('label.bic')"
                            hide-details
                        >
                            <span slot="append">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            v-html="show_bic ? 'mdi-eye' : 'mdi-eye-off'"
                                            @click="show_bic = !show_bic"
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
                            v-model="form.card_number.value"
                            :type="show_card_number ? 'text' : 'password'"
                            :label="$t('label.card_number')"
                            hide-details
                        >
                            <span slot="append">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            v-html="show_card_number ? 'mdi-eye' : 'mdi-eye-off'"
                                            @click="show_card_number = !show_card_number"
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
                            v-model="form.expiration_date.value"
                            :type="show_expiration_date ? 'text' : 'password'"
                            :label="$t('label.expiration_date')"
                            hide-details
                        >
                            <span slot="append">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            v-html="show_expiration_date ? 'mdi-eye' : 'mdi-eye-off'"
                                            @click="show_expiration_date = !show_expiration_date"
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
                            v-model="form.cvc.value"
                            :type="show_cvc ? 'text' : 'password'"
                            :label="$t('label.cvc')"
                            hide-details
                        >
                            <span slot="append">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-icon
                                            v-on="on"
                                            v-bind="attrs"
                                            v-html="show_cvc ? 'mdi-eye' : 'mdi-eye-off'"
                                            @click="show_cvc = !show_cvc"
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
    name: "AddBank",
    data: () => ({
        open: false ,
        secret_id: null,
        show_iban: false,
        show_bic: false,
        show_card_number: false,
        show_expiration_date: false,
        show_cvc: false,
        loading: false,
        show: ["iban", "bic", "card_number", "expiration_date", "cvc"],
        errors: [],
        form: {
            secret_type: "bank",
            name: {encrypted: false, value: ""},
            owner: {encrypted: false, value: ""},
            bank_name: {encrypted: false, value: ""},
            iban: {encrypted: true, value: ""},
            bic: {encrypted: true, value: ""},
            card_number: {encrypted: true, value: ""},
            expiration_date: {encrypted: true, value: ""},
            cvc: {encrypted: true, value: ""},
            informations: {encrypted: false, value: ""}
        }
    }),

    computed: {
        title() {
            return this.secret_id ? this.$t('title.edit_bank') : this.$t("title.add_bank")
        }
    },

    watch: {
        open(val) {
            if (!val) {
                this.form = {
                    secret_type: "bank",
                    name: {encrypted: false, value: ""},
                    owner: {encrypted: false, value: ""},
                    bank_name: {encrypted: false, value: ""},
                    iban: {encrypted: true, value: ""},
                    bic: {encrypted: true, value: ""},
                    card_number: {encrypted: true, value: ""},
                    expiration_date: {encrypted: true, value: ""},
                    cvc: {encrypted: true, value: ""},
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
        EventBus.$on("edit_bank", (secret_id, folder_id) => {
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
                    secret_type: 'bank',
                    name: secret.name,
                    owner: secret.owner,
                    bank_name: secret.bank_name,
                    iban: secret.iban,
                    bic: secret.bic,
                    card_number: secret.card_number,
                    expiration_date: secret.expiration_date,
                    cvc: secret.cvc,
                    informations: secret.informations
                }
            }).then(() => {
                this.loading = false
            })
        },

        closePanel() {
            this.form = {
                secret_type: 'bank',
                name: "",
                owner: "",
                bank_name: "",
                iban: "",
                bic: "",
                card_number: "",
                expiration_date: "",
                cvc: "",
                informations: ""
            }
            this.show_iban = false
            this.show_bic = false
            this.open = false
        },

        async saveBank() {
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
            this.$toast.success(this.$t(message))
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
