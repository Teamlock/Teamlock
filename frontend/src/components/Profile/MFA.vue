<template>
    <span>
        <v-card flat>
            <v-card-text>
                <h3 class="factor_title_profile mb-5 mt-3">
                    {{ $t('label.two_factor') }}
                </h3>
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
                        class="btn_mfa_profile mb-4"
                        outlined
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
                                outlined
                                class="btn_mfa_profile mb-4"
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
    </span>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import VueQRCodeComponent from 'vue-qrcode-component'
import { mapGetters } from 'vuex'
import http from "@/utils/http"

export default defineComponent({
    components: {
        "qr-code": VueQRCodeComponent,
    },
    
    data: () => ({
        dialog2FA: false,
        dialogDisable2FA: false,
        loadingEnable2FA: false,
        loadingDisable2FA: false,
        loadingValidate2FA: false,
        enforce_totp: false,
        captcha: "",
        otp_value: "",
        otp_disable_value: "",
    }),

    computed: {
        ...mapGetters({
            user: 'getUser'
        })
    },

    methods: {
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
                    this.$toast.success(this.$t('success.otp_disabled'))
                })
                .catch((err) => {
                    if (err.response.status === 400) {
                        this.$toast.error(this.$t("error.invalid_otp"))
                    } else if (err.response.status === 401) {
                        this.$toast.error(this.$t("warning.otp_enforced"))
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
                    this.$toast.success(this.$t('success.otp_validated'))

                    setTimeout(() => {
                        this.$store.dispatch("set_user")
                    }, 1000);
                })
                .catch((err) => {
                    if (err.response.status === 400) {
                        this.$toast.error(this.$t("error.invalid_otp"))
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
