<template>
    <v-card flat class="justify-content">
        <v-card-text>
            <v-form
                v-if="need_configure || reset"
                @submit.prevent="validateOtp"
                class="form-configure"
            >
                <v-alert type="warning"> {{ $t("label.configure_otp") }} </v-alert>
                <qr-code :text="captcha" :size="200" class="mt-5 qr-code"/>
                <v-otp-input
                    v-model="otp_value"
                    class="mt-5"
                    length="6"
                    type="number"
                    @finish="validateOtp"
                />
                <v-btn type="submit">
                    {{ $t('label.enable_otp') }}
                </v-btn>  
            </v-form>
            <div v-else>
                <v-card flat v-if="otp_enabled">
                    <p>
                        {{ $t('label.status') }}:
                        <v-chip
                            class="ma-2"
                            color="white"
                            label
                            small
                            text-color="success"
                        >
                            {{ $t("label.enabled") }}
                        </v-chip>
                    </p>
                    <v-menu offset-y max-width="500" bottom :close-on-content-click="false">
                        <template v-slot:activator="{ on: menu, attrs }">
                            <v-tooltip bottom>
                                <template v-slot:activator="{ on: tooltip }">
                                    <v-btn
                                        v-bind="attrs"
                                        v-on="{ ...tooltip, ...menu }"
                                    >
                                        {{ $t('label.disable_otp') }}
                                    </v-btn>
                                </template>
                                <span>{{ $t("help.disable_otp") }}</span>
                            </v-tooltip>
                        </template>
                        <v-card>
                            <v-card-text>
                                <v-alert type="warning">
                                    {{ $t("help.disable_otp") }}
                                </v-alert>
                                <v-otp-input
                                    ref="disable_otp_input"
                                    v-model="otp_value"
                                    length="6"
                                    type="number"
                                />
                            </v-card-text>
                            <v-card-actions>
                                <v-spacer />
                                <v-btn small text>{{ $t('button.cancel') }}</v-btn>
                                <v-btn small color="primary" text @click="disableOtp">{{ $t('button.confirm') }}</v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-menu>
                </v-card>
                <v-card flat v-else>
                    <p>
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
                    <v-btn @click="enableOtp">{{ $t('label.enable_otp') }}</v-btn>
                </v-card>
            </div>
        </v-card-text>
    </v-card>
</template>
<script>
import { defineComponent } from '@vue/composition-api';
import VueQRCodeComponent from 'vue-qrcode-component'
import http from "@/utils/http";
import { mapGetters } from 'vuex';

export default defineComponent({
    name:"TotpConfiguration",

    components : {
        "qr-code": VueQRCodeComponent,
    },

    data : () => ({
        captcha : "",
        otp_value : "",
        otp_enabled : false,
        reset : false,
    }),

    computed: {
        ...mapGetters({
            totp_enforce : "getTotpEnforce",
            need_configure : "getNeedConfigureOtp",
            user: "getUser"
        })
    },

    beforeMount(){
        this.otp_enabled = this.user.otp.enabled;
        if(this.need_configure)this.getQrCode();
    },

    methods : {
        getQrCode(){
            http.get("/pro/api/v1/user/totp/enable").then(res => {
                this.captcha = res.data;
            });
        },
        enableOtp(){
            this.getQrCode();
            this.reset = true;
        },

        disableOtp(){
            http.post("/pro/api/v1/user/totp/disable", {totp_value: this.otp_value})
                .then(() => {
                    this.$toast.success(this.$t('success.otp_disabled'));
                    this.otp_enabled = false;
                    this.$store.dispatch("set_user");
                    this.otp_value = "";
                })
                .catch((err) => {
                    if (err.response.status === 400) {
                        this.$toast.error(this.$t("error.invalid_otp"))
                    }
                    this.otp_value = ""
                })
        },

        validateOtp(){
            http.post("/pro/api/v1/user/totp/validate", {totp_value: this.otp_value})
                .then(() => {
                    this.otp_enabled = true;
                    this.$toast.success(this.$t('success.otp_validated'));
                    this.$store.dispatch("set_user");
                    this.reset = false;
                    this.otp_value = "";
                    if(this.$route.path === "/totp"){
                        setTimeout(() => this.$router.push("/"), 1000);
                    }
                })
                .catch((err) => {
                    if (err.response.status === 400) {
                        this.$toast.error(this.$t("error.invalid_otp"))
                    }
                    this.otp_value = ""
                })
        },
    },  
})
</script>
<style scoped>
.form-configure{
    display : flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
</style>
