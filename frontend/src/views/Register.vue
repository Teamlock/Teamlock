<template>
    <v-app app :class="renderClassBG()">
        <v-container pa-0>
            <v-row align="center" justify="center" style="height: 80vh" dense>
                <v-col cols="12" lg="5" md="6">
                    <v-card
                        tile
                        elevation="10"
                        class="justify-center"
                        style="padding: 30px;"
                    >
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
                                    {{ $t("success.check_email_registration") }}
                                </v-alert>

                                <v-form ref="form" v-model="valid" @submit.prevent="register" class="v_form_login" v-if="!success">
                                    <v-text-field
                                        v-model="email"
                                        :label="$t('label.email')"
                                        :rules="[v => !!v || $t('required.email')]"
                                        required
                                    />
                                    <v-btn type="submit" :loading="is_loading" color="primary"><v-icon>mdi-log-in</v-icon> {{ $t('button.register')}}</v-btn><br/><br/>
                                </v-form>
                            </v-col>
                        </v-row>
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
    name: 'Register',
    mixins: [renderMixin],

    data: () => ({
        logo_light: require("@/assets/img/TLAppLogo_White.svg"),
        logo_dark: require("@/assets/img/TLAppLogo_Baseline.svg"),
        is_loading: false,
        valid: true,
        success: false,
        email: "",
        error: "",
    }),

    mounted() {},

    methods: {
        register() {
            this.error = ""
            this.is_loading = true
            
            const url = `${process.env.VUE_APP_BASE_URL}/api/v1/auth/register`
            const form = {
                email: this.email
            }

            axios.post(url, form).then(() => {
                this.success = true
            }).catch((err) => {
                if (err.response.status === 409) {
                    this.error = this.$t("error.unique_user")
                }
            }).then(() => {
                this.is_loading = false
            })
        }
    }
})
</script>