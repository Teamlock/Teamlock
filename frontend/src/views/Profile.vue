<template>
    <v-container>
        <v-row class="yellow_line"></v-row>

        <v-row>
            <v-col :md="8" class="mx-auto">
                <v-card>
                    <v-list class="pb-0">
                        <v-list-item class="card_pict_profile">
                            <v-list-item-avatar class="pict_profile">
                                <v-img :src="image" height="80" width="300"/>
                            </v-list-item-avatar>
                        </v-list-item>

                        <v-list-item link class="content_card_profile">
                            <v-list-item-content v-if="user">
                                <v-list-item-subtitle class="mail_profile">{{ user.email }}</v-list-item-subtitle>
                                <v-list-item-subtitle class="">{{ $t("label.last_change_password") }}: {{ renderDate(user.last_change_pass, "DD/MM/YYYY") }}</v-list-item-subtitle>
                                <v-list-item-subtitle class="mt-5">
                                    <v-btn small color="primary" text @click="downloadCertificates" :loading="downloadCertificatesLoading">
                                        <v-icon>mdi-download</v-icon>
                                        {{ $t('button.download_certificates') }}
                                    </v-btn>
                                </v-list-item-subtitle>
                            </v-list-item-content>
                        </v-list-item>
                    </v-list>
                </v-card>
            </v-col>
        </v-row>

        <v-row>
            <v-col :md="8" class="mx-auto">
                <v-form ref="form" @submit.prevent="changePassword" class>
                    <v-card :loading="loading" class="pt-0">
                        <v-app-bar flat dense class="app_bar_change_password_profile">
                            <v-toolbar-title class="pl-0 title_change_pass">
                                {{ $t('label.change_password') }}
                            </v-toolbar-title>
                        </v-app-bar>
                        <!-- CHANGE PASSWORD -->
                        <v-card-text class="pt-0">
                            <v-alert 
                                v-if="user.need_change_password"
                                type="warning"
                                border="top"
                                class="mt-4"
                            >
                                {{ $t("warning.need_change_password") }}
                            </v-alert>
                            <v-alert 
                                v-if="warning_change_password"
                                type="warning"
                                border="top"
                                class="mt-4"
                            >
                                {{ warning_change_password }}
                            </v-alert>
                            <v-text-field
                                type="password"
                                v-model="form.current_password"
                                :label="$t('label.current_password')"
                                class="input-field pl-1 pr-1 mb-2"
                                hide-details
                                color="#DAAB39"
                                required
                            />
                            <v-text-field
                                type="password"
                                v-model="form.new_password"
                                :label="$t('label.new_password')"
                                class="input-field pl-1 pr-1 mb-2"
                                :error-messages="errorPassword"
                                :error-count="errorPassword.length"
                                :hide-details="errorPassword.length === 0"
                                color="#DAAB39"
                                required
                            />
                            <v-text-field
                                type="password"
                                v-model="form.confirm_password"
                                :label="$t('label.confirm_password')"
                                class="input-field pl-1 pr-1 mb-2"
                                color="#DAAB39"
                                :error-messages="errorsFormChangePassword"
                                :hide-details="errorsFormChangePassword"
                                required
                            />

                        </v-card-text>
                        <v-card-actions>
                            <v-alert
                                type="warning"
                                dense
                                :icon="false"
                                class="mb-0"
                            >
                                <small>{{ $t('warning.remember_recovery2') }}</small>
                            </v-alert>
                            <v-spacer />
                            <v-btn
                                :loading="loading"
                                small
                                color="primary"
                                text
                                type="submit"
                            >
                                {{ $t('button.confirm') }}
                            </v-btn>
                        </v-card-actions>
                    </v-card>
                </v-form>
            </v-col>
        </v-row>
        <v-row v-if="is_pro">
            <!-- ENABLE 2FA -->
            <v-col :md="8" class="mx-auto">
                <v-card>
                    <v-app-bar flat dense>
                        <v-toolbar-title class="factor_title_profile">
                            {{ $t('label.two_factor') }}
                        </v-toolbar-title>
                    </v-app-bar>
                    <v-card-text class="text-left">
                        <span v-if="!user.otp.enabled" >
                            <p class="p_status_profile">
                                {{ $t('label.status') }}:
                                <v-chip
                                    class="ma-2 text_disable"
                                    color="white"
                                    label
                                    small
                                    text-color="#B71C1C"
                                >
                                    {{ $t("label.disabled") }}
                                </v-chip>
                            </p>
                            <v-btn
                                color="primary"
                                @click="enable2FA"
                                :loading="loadingEnable2FA"
                                class="btn_mfa_profile"
                                small
                            >
                                {{ $t('label.enable_otp') }}
                            </v-btn>
                        </span>
                        <span v-if="user.otp.enabled">
                            <p class="p_status_profile">
                                {{ $t('label.status') }}:
                                <v-chip
                                    class="ma-2 text_disable"
                                    color="white"
                                    label
                                    small
                                    text-color="success"
                                >
                                    {{ $t("label.enabled") }}
                                </v-chip>
                            </p>
                            <v-dialog width="500" v-model="dialogDisable2FA" v-if="!enforce_totp">
                                <template v-slot:activator="{ on, attrs }">
                                    <v-btn
                                        v-bind="attrs"
                                        v-on="on"
                                        color="#B71C1C"
                                        dark
                                        small
                                        class="btn_mfa_profile"
                                    >
                                        {{ $t('label.disable_otp') }}
                                    </v-btn>
                                </template>
                                <v-card>
                                    <v-card-title>
                                        {{ $t("title.2fa_disable") }}
                                    </v-card-title>
                                    <v-card-text>
                                        <v-otp-input
                                            v-model="otp_disable_value"
                                            length="6"
                                            type="number"
                                            class="mt-5"
                                        />
                                    </v-card-text>
                                    <v-card-actions>
                                        <v-spacer />
                                        <v-btn
                                            text
                                            small
                                            color="primary"
                                            :loading="loadingDisable2FA"
                                            @click="disable2FA"
                                        >
                                            {{ $t("button.validate") }}
                                        </v-btn>
                                    </v-card-actions>
                                </v-card>
                            </v-dialog>
                        </span>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <v-row>
            <v-col :md="8" class="mx-auto">
                <v-card :loading="recoveryLoading">
                    <v-app-bar flat dense>
                        <v-toolbar-title class="factor_title_profile">
                            {{ $t('label.download_recovery') }}
                        </v-toolbar-title>
                    </v-app-bar>

                    <v-card-text>
                        <v-alert 
                            v-if="!user.recovery_key_downloaded"
                            type="warning"
                            border="top"
                            class="mt-0"
                        >
                            {{ $t("warning.reminder_download_recovery") }}
                        </v-alert>
                        <p><b>{{ $t("help.recovery") }}<br/>{{ $t("help.recovery2") }}</b></p>
                        <v-btn :loading="recoveryLoading" @click="downloadRecovery" color="primary" small>
                            <v-icon>mdi-download</v-icon> {{ $t("label.download") }}
                        </v-btn>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>

        <v-dialog v-model="dialog2FA" width="500">
            <v-card>
                <v-card-title>
                    {{ $t("title.2fa_setup") }}
                </v-card-title>

                <v-card-text class="text-center">
                    {{ $t("help.2fa") }}
                    <qr-code :text="captcha" :size="200" class="mt-5 qr-code"/>

                    <v-otp-input
                        v-model="otp_value"
                        class="mt-5"
                        length="6"
                        type="number"
                    />                                        
                </v-card-text>
                <v-card-actions>
                    <v-spacer />
                    <v-btn
                        text
                        small
                        color="primary"
                        :loading="loadingValidate2FA"
                        @click="validate2FA"
                    >
                        {{ $t("button.validate") }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>

<script>
import VueQRCodeComponent from 'vue-qrcode-component'
import { defineComponent } from '@vue/composition-api'
import renderMixin from "@/mixins/render"
import { mapGetters } from 'vuex'
import http from "@/utils/http"

export default defineComponent({
    mixins: [renderMixin],

    components: {
        "qr-code": VueQRCodeComponent
    },

    data: () => ({
        loading: false,
        recoveryLoading: false,
        warning_change_password: "",
        dialog2FA: false,
        downloadCertificatesLoading: false,
        dialogDisable2FA: false,
        loadingEnable2FA: false,
        loadingDisable2FA: false,
        loadingValidate2FA: false,
        enforce_totp: false,
        is_pro: false,
        errorPassword: [],
        captcha: "",
        otp_value: "",
        otp_disable_value: "",
        form: {
            current_password: "",
            new_password: "",
            confirm_password: ""
        },
        errorsFormChangePassword: "",
        image: require("@/assets/img/man.svg"),
    }),
    computed: {
        ...mapGetters({
            user: 'getUser'
        })
    },

    beforeMount() {
        this.is_pro = this.$store.state.pro
        if (this.is_pro) {
            this.getProConfig()
        }
    },

    mounted() {
        setTimeout(() => {
            if (this.user.need_change_password) {
                this.$toast.warning(this.$t("warning.need_change_password"), {
                    position: "top-center",
                    timeout: 10000
                })
            }
        }, 200);
    },

    methods: {
        getProConfig() {
            http.get("/pro/api/v1/config/").then((response) => {
                this.enforce_totp = response.data.enforce_totp
            })
        },

        downloadCertificates() {
            this.downloadCertificatesLoading = true
            http.get("/api/v1/user/certificates").then((response) => {
                const fileURL = window.URL.createObjectURL(new Blob([response.data]));
                const fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', 'certificate.teamlock.pem');
                document.body.appendChild(fileLink);
                fileLink.click();
            }).catch((err) => {
                throw err
            }).then(() => {
                this.downloadCertificatesLoading = false
            })
        },

        downloadRecovery() {
            this.recoveryLoading = true
            http.get("/api/v1/user/recovery").then((response) => {
                const fileURL = window.URL.createObjectURL(new Blob([response.data]));
                const fileLink = document.createElement('a');
                fileLink.href = fileURL;
                fileLink.setAttribute('download', 'recovery.tl');
                document.body.appendChild(fileLink);
                fileLink.click();
            }).catch((err) => {
                throw err
            }).then(() => {
                this.recoveryLoading = false
            })
        },

        changePassword() {
            this.warning_change_password = ""
            if (this.form.new_password !== this.form.confirm_password) {
                this.errorsFormChangePassword = "Passwords mismatch"
                return
            }

            this.loading = true
            http.put("/api/v1/user", this.form).then(() => {
                this.$toast.success(this.$t("success.password_changed"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })

                setTimeout(() => {
                    sessionStorage.clear()
                    this.$router.push("/login")
                }, 1000);
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
                    if (error.response.data.detail === "Invalid password") {
                        this.warning_change_password = this.$t("error.invalid_password")
                    } else if (error.response.data.detail === "Used password") {
                        this.warning_change_password = this.$t("warning.already_used_password")
                    } else {
                        let detail = [error.response.data.detail.error]
                        for (const {type, min} of error.response.data.detail.details) {
                            detail.push(`${mapping[type]}: ${min}`)
                        }
    
                        this.errorPassword = detail
                        this.errorPasswordCount = detail.length + 1
                    }
                }
            }).then(() => {
                this.loading = false
            })
        },

        enable2FA() {
            this.loadingEnable2FA = true
            http.get("/pro/api/v1/user/totp/enable").then((response) => {
                this.captcha = response.data
                this.dialog2FA = true;
                this.loadingEnable2FA = false
            })
        },

        disable2FA() {
            this.loadingDisable2FA = true
            http.post("/pro/api/v1/user/totp/disable", {totp_value: this.otp_disable_value})
                .then(() => {
                    this.$store.dispatch("set_user")
                    this.dialogDisable2FA = false
                    this.$toast.success(this.$t('success.otp_disabled'), {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })
                })
                .catch((err) => {
                    if (err.response.status === 400) {
                        this.$toast.error(this.$t("error.invalid_otp"), {
                            closeOnClick: true,
                            timeout: 3000,
                            icon: true
                        })
                    } else if (err.response.status === 401) {
                        this.$toast.error(this.$t("warning.otp_enforced"), {
                            closeOnClick: true,
                            timeout: 3000,
                            icon: true
                        })
                    }
                })
                .then(() => {
                    this.otp_disable_value = ""
                    this.loadingDisable2FA = false
                })
        },

        validate2FA() {
            this.loadingValidate2FA = true
            http.post("/pro/api/v1/user/totp/validate", {totp_value: this.otp_value})
                .then(() => {
                    this.dialog2FA = false
                    this.$toast.success(this.$t('success.otp_validated'), {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })

                    setTimeout(() => {
                        this.$store.dispatch("set_user")
                    }, 1000);
                })
                .catch((err) => {
                    if (err.response.status === 400) {
                        this.$toast.error(this.$t("error.invalid_otp"), {
                            closeOnClick: true,
                            timeout: 3000,
                            icon: true
                        })
                    }
                })
                .then(() => {
                    this.otp_value = ""
                    this.loadingValidate2FA = false
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
        padding-left: 5px;
    }
</style>
