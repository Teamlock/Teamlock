<template>
    <v-app app class="background_auth">
        <v-container pa-0>
            <v-row align="center" justify="center" style="height: 80vh" dense>
                <v-col cols="12" lg="8" md="8">
                    <v-card
                        tile
                        elevation="10"
                        :loading="is_loading"
                        style="padding: 0 20px 20px 20px"
                    >
                        <img v-if="$vuetify.theme.dark" :src="logo_light" id="logo" height="150" width="500"/>
                        <img v-else :src="logo_dark" id="logo" height="150" width="500"/>
                        <h1>{{ $t("title.installation") }}</h1>

                        <v-alert
                            v-if="warning"
                            type="warning"
                            border="top"
                            class="mt-4"
                        >
                            {{ warning }}
                        </v-alert>

                        <v-card-title class="text-h6 font-weight-regular justify-space-between">
                            <span>{{ currentTitle }}</span>
                        </v-card-title>
                        <v-card-text class="text-left mb-10">
                            <v-window v-model="step" width="70%">
                                <v-window-item :value="1">
                                    <v-card-text>
                                        <v-row dense>
                                            <v-col>
                                                <label>{{ $t('label.rsa_key_size') }}</label>
                                                <v-slider
                                                    v-model="form.config_schema.rsa_key_size"
                                                    max="8192"
                                                    step="2048"
                                                    min="0"
                                                    tabindex="-1"
                                                    hide-details
                                                    track-color="#E2E2E2"
                                                >
                                                    <template v-slot:append>
                                                        <v-text-field
                                                            v-model="form.config_schema.rsa_key_size"
                                                            class="mt-0 pt-0"
                                                            hide-details
                                                            single-line
                                                            type="number"
                                                            style="width: 60px"
                                                        />
                                                    </template>
                                                </v-slider>
                                            </v-col>
                                        </v-row>
                                        <v-row dense v-if="is_pro">
                                            <v-col>
                                                <v-switch
                                                    v-model="form_pro.enforce_totp"
                                                    :label="$t('label.enforce_totp')"
                                                    :hint="$t('help.enforce_totp')"
                                                    persistent-hint
                                                />
                                            </v-col>
                                        </v-row>
                                        <v-row dense>
                                            <v-col>
                                                <v-switch
                                                    v-model="form.config_schema.allow_self_registration"
                                                    :label="$t('label.allow_self_registration')"
                                                    :hint="$t('help.allow_self_registration')"
                                                    persistent-hint
                                                />
                                            </v-col>
                                        </v-row>
                                        <v-row dense v-if="form.config_schema.allow_self_registration">
                                            <v-col>
                                                <v-combobox
                                                    v-model="form.config_schema.allowed_email_addresses"
                                                    :items="[]"
                                                    append-icon=""
                                                    :label="$t('label.allowed_email_addresses')"
                                                    :hint="$t('help.allowed_email_addresses')"
                                                    persistent-hint
                                                    multiple
                                                    chips
                                                >
                                                    <template v-slot:selection="{ attrs, item, parent, selected }">
                                                        <v-chip
                                                            v-bind="attrs"
                                                            color="primary"
                                                            :input-value="selected"
                                                            label
                                                            small
                                                        >
                                                        <span class="pr-2">
                                                            {{ item }}
                                                        </span>
                                                        <v-icon
                                                            small
                                                            @click="parent.selectItem(item)"
                                                        >
                                                            $delete
                                                        </v-icon>
                                                        </v-chip>
                                                    </template>
                                                </v-combobox>
                                            </v-col>
                                        </v-row>
                                    </v-card-text>
                                </v-window-item>

                                <v-window-item :value="2">
                                    <v-card-text>
                                        <v-row>
                                            <v-col :md="12">
                                                <label>{{ $t('label.password_duration') }}</label>
                                                <v-slider
                                                    tabindex="-1"
                                                    v-model="form.config_schema.password_duration"
                                                    max="365"
                                                    step="1"
                                                    min="1"
                                                    :hint="$t('help.password_duration')"
                                                    persistent-hint
                                                    class="mb-0 pb-0"
                                                    track-color="#E2E2E2"
                                                >
                                                    <template v-slot:append>
                                                        <v-text-field
                                                            v-model="form.config_schema.password_duration"
                                                            class="mt-0 pt-0"
                                                            single-line
                                                            type="number"
                                                            style="width: 60px"
                                                        />
                                                    </template>
                                                </v-slider>
                                            </v-col>
                                        </v-row>
                                        <v-row>
                                            <v-col class="text-left">
                                                <label>{{ $t('label.password_length') }}</label>
                                                <v-slider
                                                    tabindex="-1"
                                                    v-model="form.config_schema.password_policy.length"
                                                    max="100"
                                                    min="0"
                                                    track-color="#E2E2E2"
                                                >
                                                    <template v-slot:append>
                                                        <v-text-field
                                                            v-model="form.config_schema.password_policy.length"
                                                            class="mt-0 pt-0"
                                                            hide-details
                                                            single-line
                                                            type="number"
                                                            style="width: 60px"
                                                        />
                                                    </template>
                                                </v-slider>
                                            </v-col>
                                            <v-col class="text-left">
                                                <label>{{ $t('label.password_upper') }}</label>
                                                <v-slider
                                                    tabindex="-1"
                                                    v-model="form.config_schema.password_policy.uppercase"
                                                    :max="form.config_schema.password_policy.length"
                                                    min="0"
                                                    track-color="#E2E2E2"
                                                >
                                                    <template v-slot:append>
                                                        <v-text-field
                                                            v-model="form.config_schema.password_policy.uppercase"
                                                            class="mt-0 pt-0"
                                                            hide-details
                                                            single-line
                                                            type="number"
                                                            style="width: 60px"
                                                        />
                                                    </template>
                                                </v-slider>
                                            </v-col>
                                        </v-row>
                                        <v-row dense>
                                            <v-col class="text-left">
                                                <label>{{ $t('label.password_number') }}</label>
                                                <v-slider
                                                    tabindex="-1"
                                                    v-model="form.config_schema.password_policy.numbers"
                                                    :max="form.config_schema.password_policy.length - form.config_schema.password_policy.uppercase"
                                                    min="0"
                                                    track-color="#E2E2E2"
                                                >
                                                    <template v-slot:append>
                                                        <v-text-field
                                                            v-model="form.config_schema.password_policy.numbers"
                                                            class="mt-0 pt-0"
                                                            hide-details
                                                            single-line
                                                            type="number"
                                                            style="width: 60px"
                                                        />
                                                    </template>
                                                </v-slider>
                                            </v-col>
                                            <v-col class="text-left">
                                                <label>{{ $t('label.password_special') }}</label>
                                                <v-slider
                                                    tabindex="-1"
                                                    v-model="form.config_schema.password_policy.special"
                                                    :max="form.config_schema.password_policy.length - (form.config_schema.password_policy.uppercase + form.config_schema.password_policy.numbers)"
                                                    min="0"
                                                    track-color="#E2E2E2"
                                                >
                                                    <template v-slot:append>
                                                        <v-text-field
                                                            v-model="form.config_schema.password_policy.special"
                                                            class="mt-0 pt-0"
                                                            hide-details
                                                            single-line
                                                            type="number"
                                                            style="width: 60px"
                                                        />
                                                    </template>
                                                </v-slider>
                                            </v-col>
                                        </v-row>
                                    </v-card-text>
                                </v-window-item>

                                <v-window-item :value="3">
                                    <v-card-text>
                                        <v-row dense>
                                            <v-col>
                                                <v-text-field
                                                    v-model="form.admin.email"
                                                    :label="$t('label.email')"
                                                    color="#DAAB39"
                                                    class="pl-1 pr-1 mb-2"
                                                    :error-messages="errorEmail"
                                                    :hide-details="errorEmail.length === 0"
                                                />
                                            </v-col>
                                        </v-row>
                                    </v-card-text>
                                </v-window-item>
                            </v-window>
                        </v-card-text>

                        <v-spacer />

                        <v-card-actions class="card-actions">
                            <v-spacer />
                            <v-btn
                                :disabled="step === 1"
                                text
                                class="mr-2"
                                @click="changeStep('-')"
                            >
                                {{ $t("button.back") }}
                            </v-btn>
                            <v-btn
                                v-if="step < 3"
                                color="primary"
                                depressed
                                @click="changeStep('+')"
                            >
                                {{ $t("button.next") }}
                            </v-btn>
                            <v-btn
                                v-if="step === 3"
                                color="primary"
                                depressed
                                @click="install"
                                :loading="is_loading"
                            >
                                {{ $t("button.install") }}
                            </v-btn>
                            <v-spacer />
                        </v-card-actions>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </v-app>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import axios from "axios"

export default defineComponent({
    name: 'Auth',

    data: () => ({
        logo_light: require("@/assets/img/TLAppLogo_White.svg"),
        logo_dark: require("@/assets/img/TLAppLogo_Baseline.svg"),
        step: 1,
        is_loading: false,
        valid: true,
        success: false,
        is_pro: false,
        warning: "",
        errorEmail: [],
        error: "",

        form: {
            config_schema: {
                password_policy: {
                    length: 12,
                    uppercase: 1,
                    numbers: 1,
                    special: 1  
                },
                rsa_key_size: 4096,
                password_duration: 100,
                allow_self_registration: false,
                allowed_email_addresses: [],
            },
            admin: {
                email: "",
                password: "",
                confirm_password: ""
            }
        },

        form_pro: {
            enforce_totp: false,
        }
    }),

    computed: {
      currentTitle () {
        switch (this.step) {
          case 1: return this.$t('label.general_configuration')
          case 2: return this.$t('label.password_configuration')
          default: return this.$t('label.admin_configuration')
        }
      }
    },

    beforeMount() {
        axios.get(`${process.env.VUE_APP_BASE_URL}/pro/`).then(() => {
            this.is_pro = true
        }).catch(() => {})
    },

    methods: {
        changeStep(to) {
            if (to === "+") {
                let valid = true
                switch(this.step) {
                    case 1:
                        if (this.form.config_schema.allow_self_registration) {
                            // If registration is enabled, user must provide email addresses
                            if (this.form.config_schema.allowed_email_addresses.length === 0) {
                                this.warning = this.$t("error.provide_allowed_email_addresses")
                                valid = false
                            } else {
                                const regex = new RegExp('@[a-z]+.[a-z]{2,3}');
                                for (const dom of this.form.config_schema.allowed_email_addresses) {
                                    if (!regex.test(dom)) {
                                        this.warning = `${this.$t("error.invalid_domain")}: ${dom}`
                                        valid = false
                                    }
                                }
                            }
                        }
                        break
                }

                if (valid) {
                    this.step++
                }
            } else if (to === "-") {
                this.step--
            }
        },

        async install() {
            this.errorEmail = []
            this.errorPassword = []

            if (this.form.admin.password !== this.form.admin.confirm_password) {
                this.warning = this.$t("error.password_mismatch")
                return
            }

            this.is_loading = true
            if (this.is_pro) {
                const pro_url = `${process.env.VUE_APP_BASE_URL}/pro/api/v1/config/install`
                await axios.post(pro_url, this.form_pro)
            }

            const url = `${process.env.VUE_APP_BASE_URL}/install`
            axios.post(url, this.form).then(async () => {
                this.$toast.success(this.$t("success.successful_installation"))

                setTimeout(() => {
                    this.$router.push({name: "Login"})
                }, 1000)
            }).catch((error) => {
                try {
                    if (error.response.status === 400) {
                        if (error.response.data.detail === "INVALIDEMAIL") {
                            this.errorEmail.push(this.$t("error.invalid_domain"))
                            return
                        }
                    }
                } catch(err) {
                    console.error(err)
                    this.$toast.error(this.$t("error.occurred"))
                }
            }).then(() => {
                this.is_loading = false
            })
        }
    }
})
</script>

<style scoped>
    @font-face {
        font-family: "Coolvetica";
        src: url("../assets/fonts/coolvetica condensed rg.otf") format("woff2"),
    }

    .input-field >>> input{
        background-color: #F5F5F5!important;
        padding-left: 5px;
    }
</style>
