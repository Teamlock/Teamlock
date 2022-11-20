<template>
    <v-form ref="form" @submit.prevent="changePassword" class>
        <v-card flat>
            <v-card-text>
                <v-row>
                    <v-col :md="8" class="">
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
                    </v-col>
                </v-row>
            
                <v-row>
                    <v-col :md="8" class="">
                        <v-row>
                            <v-col :md="8">
                                <v-alert
                                    type="warning"
                                    :icon="false"
                                    dense
                                >
                                    <small>{{ $t('warning.remember_recovery2') }}</small>
                                </v-alert>
                            </v-col>
                            <v-col :md="4">
                                <v-btn
                                    :loading="loading"
                                    color="primary"
                                    class="float-right"
                                    outlined
                                    type="submit"
                                >
                                    {{ $t('button.confirm') }}
                                </v-btn>
                            </v-col>
                        </v-row>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-form>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import { mapGetters } from 'vuex'
import http from "@/utils/http"

export default defineComponent({
    data: () => ({
        warning_change_password: "",
        errorsFormChangePassword: "",
        errorPassword: [],
        loading: false,
        form: {
            current_password: "",
            new_password: "",
            confirm_password: ""
        },
    }),

    computed: {
        ...mapGetters({
            user: 'getUser'
        })
    },

    mounted() {
    },

    methods: {
        changePassword() {
            this.warning_change_password = ""
            if (this.form.new_password !== this.form.confirm_password) {
                this.errorsFormChangePassword = "Passwords mismatch"
                return
            }

            this.loading = true
            http.put("/api/v1/user", this.form).then(() => {
                this.$toast.success(this.$t("success.password_changed"))

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
    }
})
</script>
