<template>
    <v-app app :class="renderClassBG()">
        <v-container pa-0>
            <v-row align="center" justify="center" style="height:80vh" dense>
                <v-col cols="12" lg="5" md="6">
                    <v-card
                        tile
                        elevation="10"
                        class="justify-center"
                        style="padding: 30px;"
                    >
                        <v-card-text>
                            <v-row class="text-center">
                                <v-col>
                                    <img v-if="$vuetify.theme.dark" :src="logo_light"/>
                                    <img v-else :src="logo_dark"/>

                                    <v-alert
                                        v-if="error"
                                        type="error"
                                        border="top"
                                        class="mt-4"
                                    >
                                        {{ error }}
                                    </v-alert>
                                    <v-alert
                                        v-if="success"
                                        type="success"
                                        border="top"
                                        class="mt-4"
                                    >
                                        {{ $t("success.account_recovered") }}
                                    </v-alert>

                                    <v-alert
                                        dark
                                        border="top"
                                        type="warning"
                                        class="mt-4"
                                        v-if="!error && !success"
                                        prominent
                                        block
                                    >
                                        {{ $t('warning.user_recovery') }}<br/>
                                        {{ $t('warning.user_recovery2') }}
                                    </v-alert>

                                    <v-form ref="form" v-model="valid" @submit.prevent="recover" class="v_form_login" v-if="!success">
                                        <v-file-input
                                            show-size
                                            counter
                                            multiple
                                            ref="recoveryFile"
                                            v-model="file"
                                            :label="$t('label.recovery_file')"
                                        />
                                        <v-text-field
                                            v-model="email"
                                            :label="$t('label.email')"
                                            hide-details
                                            :rules="[v => !!v || $t('required.email')]"
                                            required
                                        />
                                        <v-text-field
                                            v-model="new_password"
                                            :label="$t('label.new_password')"
                                            :rules="[v => !!v || $t('required.required')]"
                                            :error-messages="errorPassword"
                                            :error-count="errorPassword.length"
                                            :hide-details="errorPassword.length === 0"
                                            type="password"
                                            required
                                        />
                                        <v-text-field
                                            v-model="confirm_password"
                                            :rules="[v => !!v || $t('required.required')]"
                                            :label="$t('label.confirm_password')"
                                            type="password"
                                            required
                                        />
                                        <v-btn type="submit" :loading="is_loading" color="primary">
                                            <v-icon class="mr-1">mdi-account-reactivate</v-icon>
                                            {{ $t('button.recover')}}
                                        </v-btn>

                                        <br/><br/>

                                        <router-link
                                            text
                                            class="mb-0"
                                            :to="{name: 'Login'}"
                                        >
                                            {{ $t("button.login") }}
                                        </router-link>
                                    </v-form>
                                </v-col>
                            </v-row>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </v-app>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import renderMixin from "@/mixins/render"
import axios from "axios"

export default defineComponent({
    name: 'Recover',
    mixins: [renderMixin],

    data: () => ({
        logo_light: require("@/assets/img/TLAppLogo_White.svg"),
        logo_dark: require("@/assets/img/TLAppLogo_Baseline.svg"),
        errorPassword: [],
        is_loading: false,
        success: false,
        valid: true,
        email: "",
        new_password: "",
        confirm_password: "",
        file: null,
        error: ""
    }),

    methods: {
        recover() {
            if (!this.file) return
            if (!this.email) return
            if (!this.new_password) return
            if (!this.confirm_password) return

            if (this.new_password !== this.confirm_password) {
                this.$toast.error(this.$t("error.passwords_mismatch"), {
                    closeOnClick: true,
                    timeout: 5000,
                    icon: true
                })
                return
            }

            this.error = ""
            this.is_loading = true
            this.errorPassword = []

            const url = `${process.env.VUE_APP_BASE_URL}/api/v1/auth/recover`

            const formData = new FormData()
            formData.append("recover_file", this.file[0])
            formData.append("email", this.email)
            formData.append("new_password", this.new_password)
            formData.append("confirm_password", this.confirm_password)

            const headers = {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            }

            axios.post(url, formData, headers).then(() => {
                this.success = true
            }).catch((error) => {
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
                    if (error.response.data.detail === "Passwords mismatch") {
                        this.$toast.error(this.$t("error.passwords_mismatch"), {
                            closeOnClick: true,
                            timeout: 5000,
                            icon: true
                        })
                    } else if (error.response.data.detail === "Invalid Recovery Key") {
                        this.$toast.error(this.$t("error.invalid_recovery_key"), {
                            closeOnClick: true,
                            timeout: 5000,
                            icon: true
                        })
                    } else {
                        let detail = [error.response.data.detail.error]
                        for (const {type, min} of error.response.data.detail.details) {
                            detail.push(`${mapping[type]}: ${min}`)
                        }

                        this.errorPassword = detail
                        this.errorPasswordCount = detail.length + 1
                    }
                } else if (error.response.status === 403) {
                    this.$toast.error(this.$t("error.not_allowed"), {
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