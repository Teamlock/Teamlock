<template>
    <v-dialog
        :loading="is_loading"
        max-width="500"
        v-model="open"
        persistent
    >
        <v-form ref="form" @submit.prevent="send_by_sms">
            <v-card>
                <v-card-title class="text-h5">
                    <v-icon class="mr-2">mdi-message-processing</v-icon>
                    {{ $t('label.send_by_sms') }}
                </v-card-title>
                <v-card-text>
                    <v-alert color="primary">
                        {{ $t('help.send_by_sms' )}}
                    </v-alert>
                    <v-row dense class="mb-4">
                        <v-text-field 
                            v-model="form.sms_to"
                            :label="$t('label.sms_recipient')"
                            color="#DAAB39"
                            ref="mail_input"
                            :hint="$t('help.twilio_recipient')"
                            persistent-hint
                            required
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
        key_id: {
            type: String,
            required: false
        },
    },

    data: () => ({
        is_loading: false,
        open: false,
        form: {
            sms_to: ""
        }
    }),

    methods: {
        send_by_sms() {
            this.is_loading = true
            http.post(`/pro/api/v1/key/${this.key_id}/send/sms`, this.form)
                .then(() => {
                    this.$toast.success(this.$t('success.secret_shared'), {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })
                    this.form.sms_to = ""
                    this.open = false
                })
                .catch((error) => {
                    this.$toast.error(error.response.data.detail, {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })
                })
                .then(() => {
                    this.is_loading = false
                })
        }
    }
})
</script>
