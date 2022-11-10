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
                                    <img v-if="$vuetify.theme.dark" :src="logo_light" width="100%"/>
                                    <img v-else :src="logo_dark" width="100%"/>

                                    <v-alert
                                        v-if="error"
                                        type="error"
                                        border="top"
                                        class="mt-2"
                                    >
                                        {{ error }}
                                    </v-alert>

                                    <v-form ref="form" v-model="valid" @submit.prevent="login" v-if="!need_otp && !hasToConfigureOTP" class="v_form_login">
                                        <v-text-field
                                            v-if="electron"
                                            v-model="form.teamlock_url"
                                            :label="$t('label.teamlock_url')"
                                            :rules="[v => !!v || $t('required.teamlock_url')]"
                                            ref="teamlock_url"
                                            required
                                        />
                                        <v-text-field
                                            v-model="form.username"
                                            type="email"
                                            :label="$t('label.email')"
                                            :rules="[v => !!v || $t('required.email')]"
                                            ref="email"
                                            required
                                        />
                                        <v-text-field
                                            type="password"
                                            ref="password"
                                            :rules="[v => !!v || $t('required.password')]"
                                            v-model="form.password"
                                            :label="$t('label.password')"
                                            required
                                        />
                                        <v-checkbox
                                            v-if="electron && capabilities.touchID"
                                            v-model="useBiometric"
                                            :label="$t('label.use_biometric')"
                                        />

                                        <v-btn type="submit" :loading="is_loading" color="primary">
                                            <v-icon>mdi-log-in</v-icon>
                                            {{ $t('button.login')}}
                                        </v-btn>
                                    </v-form>
                                    <v-form ref="formOtp" v-model="otpValid" @submit.prevent="validateOTP" v-if="need_otp || hasToConfigureOTP">
                                        <v-alert
                                            v-if="error_otp"
                                            type="error"
                                            border="top"
                                            class="mt-4"
                                        >
                                            {{ error_otp }}
                                        </v-alert>
                                        <v-alert
                                            v-if="hasToConfigureOTP"
                                            type="warning"
                                            border="top"
                                            class="mt-4"
                                        > {{$t("label.configure_otp")}} </v-alert>

                                        <qr-code :text="captcha" :size="200" class="mt-5 qr-code" v-if="hasToConfigureOTP"/>
                                        <p class="mt-5" v-if="!hasToConfigureOTP">{{ $t('help.otp') }}</p>

                                        <v-otp-input length="6" v-model="form.otp" ref="otp" :label="$t('label.otp')" class="mt-5 mb-5" @finish="validateOTP"/>

                                        <v-checkbox v-model="rememberOTP" :label="$t('label.remember_otp')"/>
                                        <v-btn type="submit" :loading="is_loading_otp" color="primary">
                                            <v-icon>mdi-log-in</v-icon>
                                            {{ $t('button.submit') }}
                                        </v-btn>
                                    </v-form>
                                </v-col>
                            </v-row>
                        </v-card-text>
                        <v-card-actions>
                            <router-link 
                                v-if="self_registration"
                                text
                                :to="{name: 'Registration'}"
                            >
                                {{ $t("button.register") }}
                            </router-link>

                            <v-spacer v-if="self_registration" />

                            <router-link 
                                text
                                :to="{name: 'Recover'}"
                            >
                                {{ $t("button.recover") }}
                            </router-link>
                        </v-card-actions>
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
import qs from "qs"
import VueQRCodeComponent from 'vue-qrcode-component'

export default defineComponent({
    name: 'Auth',
    mixins: [renderMixin],
    components: {
        "qr-code": VueQRCodeComponent,
    },

    data: () => ({
        logo_light: require("@/assets/img/TLAppLogo_White.svg"),
        logo_dark: require("@/assets/img/TLAppLogo_Baseline.svg"),
        self_registration: false,
        is_loading_otp: false,
        is_loading: false,
        electron: false,
        useBiometric: false,
        need_otp: false,
        valid: true,
        otpValid: true,
        capabilities: {
            touchID: false
        },
        rememberOTP: false,
        form: {
            teamlock_url: "",
            username: "",
            password: "",
            otp: ""
        },
        error: "",
        error_otp: "",
        hasToConfigureOTP: false,
    }),

    async beforeMount() {
        const userAgent = navigator.userAgent.toLowerCase();
        this.electron = userAgent.indexOf(' electron/') > -1

        if (!this.electron) {
            const url = `${process.env.VUE_APP_BASE_URL}/api/v1/config/registration`
            const response = await axios.get(url)
            this.self_registration = response.data

        } else {
            window.ipc.on("CAPABILITIES", (capabilities) => {
                this.capabilities = capabilities
            })
            window.ipc.send("CAPABILITIES")
        }
    },

    beforeDestroy() {},

    async mounted() {
        localStorage.removeItem("current_workspace")
        const email = localStorage.getItem("teamlock_email")

        if (this.electron) {
            window.ipc.send("GET_SETTINGS")
            window.ipc.on("GET_SETTINGS", (settings) => {
                if (settings) {
                    this.form.teamlock_url = settings.teamlock_url
                    this.form.username = settings.username
                    if (this.$refs.password) {
                        this.$refs.password.focus()
                    }

                    if (this.capabilities.touchID) {
                        const encrypted_password = localStorage.getItem("ENCRYPTED_PASSWORD")
                        if (encrypted_password) {
                            window.ipc.on("ERROR_FINGERPRINT", () => {
                                this.$toast.error(this.$t('error.invalid_biometric'))
                            })
    
                            window.ipc.on("DECRYPTED_PASSWORD", ({data}) => {
                                this.form.password = data
                                this.login()
                            })
                            window.ipc.send("DECRYPT", {password: encrypted_password})
                        } else {
                            localStorage.removeItem("ENCRYPTED_PASSWORD")
                        }
                    }
                }
            })
        }

        if (!email){
            this.$refs.email.focus()
        } else {
            this.form.username = email
            this.$refs.password.focus()
        }
    },

    methods: {
        validateOTP() {
            this.error_otp = ""
            if (!this.form.otp) return

            if (isNaN(parseInt(this.form.otp))) return
            
            this.is_loading_otp = true;
            const headers = {
                "X-Token": sessionStorage.getItem("x_token")
            }

            let base_url = process.env.VUE_APP_BASE_URL
            if (this.electron) {
                base_url = this.form.teamlock_url
            }

            let url = `${base_url}/pro/api/v1/auth/otp`
            if (this.rememberOTP) {
                url += "?remember=true"
            }

            axios.post(url, parseInt(this.form.otp), {
                headers: headers
            }).then((response) => {
                const access_token = response.data.access_token;
                sessionStorage.setItem("token", access_token)
                localStorage.setItem("teamlock_email", this.form.username)

                if (response.data.remember_key) {
                    localStorage.setItem("auth_key", response.data.remember_key)
                }

                if (this.useBiometric) {
                    window.ipc.on("ENCRYPTED_PASSWORD", ({ data }) => {
                        localStorage.setItem("ENCRYPTED_PASSWORD", data)
                    })

                    window.ipc.send("FINGERPRINT", {password: this.form.password})
                }

                this.$store.dispatch("set_user")

                let path = sessionStorage.getItem("redirectPath")
                sessionStorage.removeItem("redirectPath")
                if (!path) {
                    path = "/"
                }
                
                this.$router.push(path)
            }).catch((error) => {
                this.error_otp = error.response.data.detail
            }).then(() => {
                this.is_loading_otp = false;
            })
        },

        async login() {
            this.error = ""
            // if (!this.$refs.form.validate()) return

            if (!this.form.username || !this.form.password) {
                return
            }

            this.is_loading = true
            let base_url = process.env.VUE_APP_BASE_URL
            if (this.electron) {
                base_url = this.form.teamlock_url
            }

            const url = `${base_url}/api/v1/auth/token`
            const headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Teamlock-Key": localStorage.getItem("auth_key")
            }

            axios.post(url, qs.stringify(this.form), {
                headers: headers
            }
            ).then(async (response) => {
                if (this.electron) {
                   localStorage.setItem("teamlock_url", this.form.teamlock_url)
                    window.ipc.send("SET_SETTINGS", {
                        teamlock_url: this.form.teamlock_url,
                        username: this.form.username
                    })
                    base_url = this.form.teamlock_url

                    if (!response.data.otp && this.useBiometric) {
                        window.ipc.on("ENCRYPTED_PASSWORD", ({ data }) => {
                            localStorage.setItem("ENCRYPTED_PASSWORD", data)
                        })

                        window.ipc.send("FINGERPRINT", {password: this.form.password})
                    }
                }

                if (response.data.otp) {
                    localStorage.removeItem("auth_key")
                    sessionStorage.setItem("x_token", response.data.token)
                    if(response.data.otp_to_configure === true){
                        this.getQRCode()
                    }else{
                        this.need_otp = true;
                        this.$nextTick(() => {
                            this.$refs.otp.focus()
                        })
                    }
                } else {
                    const access_token = response.data.access_token
                    sessionStorage.setItem("token", access_token)
                    localStorage.setItem("teamlock_email", this.form.username)

                    this.$store.dispatch("set_user")

                    this.$nextTick(() => {
                        let path = sessionStorage.getItem("redirectPath")
                        sessionStorage.removeItem("redirectPath")
                        if (!path) {
                            path = "/"
                        }
                        
                        this.$router.push(path)
                    })
                }
            }).catch((error) => {
                error = error.response.data.detail;
                if (error === "Too many authentication failures") {
                    this.error = this.$t("error.too_many_auth_failures")
                } else if (error === "Could not validate credentials") {
                    this.error = this.$t("error.could_not_validate_credentials")
                } else {
                    this.error = this.$t(error)
                }
            }).then(() => {
                this.is_loading = false
            })
        },

        getQRCode(){
            let unique_code = this.$route.query.unique_code;
            if(!unique_code){
                this.error = this.$t("error.invalid_unique_code")
                return;
            }
            this.is_loading_otp = true;
            const headers = {
                "X-Token": sessionStorage.getItem("x_token")
            };
            const params = {unique_code};

            let base_url = process.env.VUE_APP_BASE_URL;
            if (this.electron) {
                base_url = this.form.teamlock_url
            }

            let url = `${base_url}/pro/api/v1/user/totp/reset`;
            axios.get(url, { params, headers }).then(response => {
                this.is_loading_otp = false;
                this.captcha = response.data
                this.hasToConfigureOTP = true
            }).catch(() => {
                this.error = this.$t("error.invalid_unique_code")
            });
        },
    }
})
</script>