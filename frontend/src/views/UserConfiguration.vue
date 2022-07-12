<template>
    <v-app :class="renderClassBG()">
        <v-card
            tile
            class="justify-center"
            width="500"
            style="margin: 5% auto; padding: 0 20px 20px 20px"
            elevation="10"
            :loading="is_loading"
        >
            <img v-if="$vuetify.theme.dark" :src="logo_light" class="mt-5"/>
            <img v-else :src="logo_dark" class="mt-5"/>

            <v-card-text class="pt-5">
                <v-row class="text-justify">
                    <v-col>
                        <v-alert
                            dark
                            border="top"
                            type="success"
                            prominent
                            block
                        >
                            {{ $t('success.registration_welcome') }}
                        </v-alert>
                        <v-alert type="error" v-if="error" v-html="error"/>
                        <v-form ref="form" v-model="valid" @submit.prevent="configure" class="v_form_login">
                            <v-text-field
                                v-model="form.email"
                                :label="$t('label.email')"
                                readonly
                                hide-details
                                required
                            />
                            <v-text-field
                                type="password"
                                ref="password"
                                :rules="[v => !!v || $t('required.required')]"
                                v-model="form.password"
                                :label="$t('label.password')"
                                required
                                class="mb-1"
                                :error-messages="errorPassword"
                                :error-count="errorPassword.length"
                                :hide-details="errorPassword.length === 0"
                            />
                            <v-text-field
                                type="password"
                                ref="confirm_password"
                                :rules="[v => !!v || $t('required.required')]"
                                v-model="form.confirm_password"
                                :label="$t('label.confirm_password')"
                                required
                            />

                            <div v-if="password_policy" class="mb-5">
                                <v-chip-group
                                    active-class="primary--text"
                                    column
                                >
                                    <v-chip
                                        v-for="(min, type) in password_policy"
                                        :key="type"
                                        label
                                        tabindex="-1"
                                        class="chip-policy"
                                        style="width: 100%"
                                    >
                                        {{ mapping[type] }}: {{ min }}
                                    </v-chip>
                                </v-chip-group>
                            </div>

                            <span v-if="captcha" class="text-justify">
                                <v-alert
                                    dark
                                    border="top"
                                    type="warning"
                                    block
                                >
                                    {{ $t('warning.otp_required') }}
                                </v-alert>

                                <qr-code :text="captcha" :size="200" class="mt-5 qr-code"/>

                                <v-otp-input
                                    v-model="form.otp_value"
                                    length="6"
                                    type="number"
                                    class="mt-5"
                                />    
                            </span>
                            <v-btn type="submit" :loading="is_loading" color="primary">
                                <v-icon>mdi-log-in</v-icon>
                                {{ $t('button.register')}}
                            </v-btn>
                        </v-form>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-app>
</template>

<script>
import VueQRCodeComponent from 'vue-qrcode-component'
import { defineComponent } from '@vue/composition-api'
import renderMixin from "@/mixins/render"
import http from "@/utils/http"

export default defineComponent({
    components: {
        "qr-code": VueQRCodeComponent
    },

    mixins: [renderMixin],

    data: (vm) => ({
        logo_light: require("@/assets/img/TLAppLogo_White.svg"),
        logo_dark: require("@/assets/img/TLAppLogo_Baseline.svg"),
        is_loading: false,
        user_id: "",
        valid: true,
        user: null,
        error: "",
        captcha: "",
        errorPassword: [],
        uri: "",
        form: {
            email: "",
            password: "",
            confirm_password: "",
            otp_value: ""
        },
        password_policy: null,
        mapping: {
            length: vm.$t("label.password_length"),
            uppercase: vm.$t("label.password_upper"),
            numbers: vm.$t("label.password_number"),
            special: vm.$t("label.password_special")
        }
    }),

    beforeMount() {
        this.user_id = this.$route.params.id
        this.uri =  `/api/v1/user/configure/${this.user_id}`
        this.checkUser()
        this.fetchPasswordPolicy()
    },

    methods: {
        async fetchPasswordPolicy() {
            try {
                const response = await http.get("/api/v1/config/policy")
                this.password_policy = response.data
            } catch (error) {
                console.error(error)
            }
        },

        configure() {
            this.is_loading = true
            this.errorPassword = []

            if (this.captcha !== "" && !this.form.otp_value) {
                this.$toast.error(this.$t("error.otp_need_config"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
            }

            const form = {
                password: this.form.password,
                confirm_password: this.form.confirm_password,
                otp_value: this.form.otp_value
            }

            const toastid = this.$toast.warning(this.$t("warning.wait_registration"), {
                position: "top-center",
                timeout: false
            })

            http.post(this.uri, form).then(() => {
                this.$toast.dismiss(toastid)

                this.$toast.success(this.$t("success.user_configured"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })

                setTimeout(() => {
                    this.$router.push({name: "Login"})
                }, 1000);
            }).catch((error) => {
                if (!error.response) {
                    return false
                }

                if (error.response.status === 400) {
                    let detail = [error.response.data.detail.error]
                    for (const {type, min} of error.response.data.detail.details) {
                        detail.push(`${this.mapping[type]}: ${min}`)
                    }

                    this.errorPassword = detail
                    this.errorPasswordCount = detail.length + 1
                }
            }).then(() => {
                this.is_loading = false
            })
        },

        checkUser() {
            http.get(this.uri).then((response) => {
                this.form.email = response.data.email
                if (response.data.otp_image) {
                    this.captcha = response.data.otp_image
                }
            }).catch((err) => {
                if (err.response.status_code === 404)
                    this.$router.push({name: "Login"})
            })
        }
    }
})
</script>
