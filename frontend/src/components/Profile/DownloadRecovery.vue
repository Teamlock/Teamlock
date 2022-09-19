<template>
    <span>
        <h3 class="factor_title_profile mt-3">
            {{ $t('label.download_recovery') }}
        </h3>

        <v-col :md="8" class="mx-auto">
            <v-alert 
                v-if="!user.recovery_key_downloaded"
                type="warning"
                border="top"
                class="mt-0"
            >
                {{ $t("warning.reminder_download_recovery") }}
            </v-alert>
        </v-col>

        <p><b>{{ $t("help.recovery") }}<br/>{{ $t("help.recovery2") }}</b></p>
        <v-btn :loading="recoveryLoading" text @click="downloadRecovery" color="primary" class="mb-2">
            <v-icon>mdi-download</v-icon> {{ $t("label.download") }}
        </v-btn>
    </span>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import { mapGetters } from 'vuex'
import http from "@/utils/http"

export default defineComponent({
    data: () => ({
        recoveryLoading: false,
    }),

    computed: {
        ...mapGetters({
            user: 'getUser'
        })
    },

    methods: {
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
        }
    }

})
</script>
