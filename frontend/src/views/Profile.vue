<template>
    <v-container fluid class="no-padding full-height">
        <v-card flat class="full-height">
            <v-tabs
                background-color="primary"
                height="40"
                dark
            >
                <v-tab>
                    <v-icon left>mdi-badge-account-horizontal</v-icon>
                    {{ $t('label.general') }}
                </v-tab>
                <v-tab>
                    <v-icon left>mdi-lock</v-icon>
                    {{ $t('label.password') }}
                </v-tab>
                <v-tab v-if="is_pro">
                    <v-icon left>mdi-cellphone-check</v-icon>
                    {{ $t('title.two_factor')}}
                </v-tab>
                <v-tab>
                    <v-icon left>mdi-account-reactivate</v-icon>
                    {{ $t('title.recovery')}}
                </v-tab>

                <v-tab-item>
                    <v-card flat class="pt-5 px-0">
                        <v-img :src="image" height="140" width="180" class="mx-auto"/>
                        <v-card-text>
                            <v-list>
                                <v-list-item>
                                    <v-list-item-content v-if="user">
                                        <v-list-item-subtitle class="mail_profile">{{ user.email }}</v-list-item-subtitle>
                                        <v-list-item-subtitle class="">{{ $t("label.last_change_password") }}: {{ renderDate(user.last_change_pass, "DD/MM/YYYY") }}</v-list-item-subtitle>
                                        <v-list-item-subtitle class="mt-5">
                                            <v-btn color="primary" outlined @click="downloadCertificates" :loading="downloadCertificatesLoading">
                                                <v-icon>mdi-download</v-icon>
                                                {{ $t('button.download_certificates') }}
                                            </v-btn>
                                        </v-list-item-subtitle>
                                    </v-list-item-content>
                                </v-list-item>
                            </v-list>
                        </v-card-text>
                    </v-card>
                </v-tab-item>
                <v-tab-item>
                    <change-password />
                </v-tab-item>
                <v-tab-item v-if="is_pro">
                    <totp-configuration/>
                </v-tab-item>

                <v-tab-item>
                    <download-recovery />
                </v-tab-item>
            </v-tabs>
        </v-card>
        <v-row class="yellow_line"></v-row>
    </v-container>
</template>

<script>
import DownloadRecovery from '../components/Profile/DownloadRecovery.vue'
import ChangePassword from '../components/Profile/ChangePassword.vue'
import TotpConfigurationVue from '../components/TotpConfiguration.vue'
import { defineComponent } from '@vue/composition-api'
import renderMixin from "@/mixins/render"
import { mapGetters } from 'vuex'
import http from "@/utils/http"

export default defineComponent({
    mixins: [renderMixin],

    components: {
        "totp-configuration" : TotpConfigurationVue,
        ChangePassword,
        DownloadRecovery
    },

    data: () => ({
        downloadCertificatesLoading: false,
        is_pro: false,
        electron: false,
        image: require("@/assets/img/man.svg"),
    }),
    computed: {
        ...mapGetters({
            user: 'getUser'
        })
    },

    beforeMount() {
        const userAgent = navigator.userAgent.toLowerCase();
        this.electron = userAgent.indexOf(' electron/') > -1
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
