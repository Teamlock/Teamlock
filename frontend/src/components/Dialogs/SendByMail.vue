<template>
    <v-dialog
        :loading="is_loading"
        max-width="500"
        v-model="open"
        persistent
    >
        <v-form ref="form" @submit.prevent="send_by_mail">
            <v-card>
                <v-card-title class="text-h5">
                    <v-icon class="mr-2">mdi-email-fast</v-icon>
                    {{ $t('label.send_by_mail') }}
                </v-card-title>
                <v-card-text>
                    <v-alert color="primary">
                        {{ $t('help.send_by_mail' )}}
                    </v-alert>
                    <v-row dense class="mb-4">
                        <v-text-field 
                            v-model="form.mail_to"
                            :label="$t('label.mail_to')"
                            type="email"
                            color="#DAAB39"
                            ref="mail_input"
                            hide-details
                            required
                        />
                    </v-row>
                    <v-row dense class="">
                        <v-text-field
                            v-model="form.expire_in"
                            :label="$t('label.expire_in')"
                            :hint="$t('help.send_by_mail_expiration')"
                            persistent-hint
                            min="1"
                            type="number"
                        />
                    </v-row>
                </v-card-text>
                <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                    text
                    small
                    @click="open = false"
                >
                    {{ $t('button.cancel') }}
                </v-btn>
                <v-btn
                    type="submit"
                    :loading="is_loading"
                    color="primary"
                    small
                    text
                >
                    {{ $t('button.send') }}
                </v-btn>
                </v-card-actions>
            </v-card>
        </v-form>
    </v-dialog>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import http from "@/utils/http"

export default defineComponent({
    props: {
        secret_id: {
            type: String,
            required: false
        },
    },

    data: () => ({
        is_loading: false,
        open: false,
        form: {
            mail_to: "oderegis@gmail.com",
            expire_in: 6
        }
    }),

    methods: {
        send_by_mail() {
            this.is_loading = true
            http.post(`/pro/api/v1/secret/${this.secret_id}/send/mail`, this.form)
                .then(() => {
                    this.$toast.success(this.$t('success.secret_shared'), {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })
                    this.is_loading = false
                    this.form.mail_to = ""
                    this.form.expire_in = 6
                    this.open = false
                })
                .catch(() => {
                    this.$toast.error(this.$t("error.occurred"), {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })
                    this.is_loading = false
                })
        }
    }
})
</script>
