<template>
    <div>
        <v-list dense v-if="data" style="text-align: left" light>
            <v-subheader>
                <v-icon style="margin-right: 5px">mdi-key</v-icon>
                <strong style="font-size: 15px">{{ data.name.value }}</strong>
            </v-subheader>
            <v-divider />
            <v-list-item-group v-model="selectedMenu">
                <v-list-item>
                    <v-list-item-icon class="mr-0">
                        <v-icon :size="17">mdi-email-fast</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('label.send_by_mail') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="sms">
                    <v-list-item-icon class="mr-0">
                        <v-icon :size="17">mdi-message-processing</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('label.send_by_sms') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list-item-group>
        </v-list>

        <send-by-mail
            ref="dialogSendByMail"
            :secret_id="secret_to_copy"
        />
        <send-by-sms
            ref="dialogSendBySMS"
            :secret_id="secret_to_copy"
        />
    </div>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import SendByMail from '../Dialogs/SendByMail.vue'
import SendBySms from '../Dialogs/SendBySMS.vue'

export default defineComponent({
    components: { 
        SendByMail,
        SendBySms
    },

    props: {
        data: {
            type: Object,
            required: false
        },
        sms: {
            type: Boolean,
            required: true
        }
    },

    data: () => ({
        selectedMenu: null,
        secret_to_copy: null
    }),

    watch: {
        selectedMenu(val) {
            if (val === null) {
                return
            }

            switch(val) {
                case 0:
                    setTimeout(() => {
                        this.$refs.dialogSendByMail.open = true
                        this.secret_to_copy = this.data._id
                    }, 100);
                    break;
                case 1:
                    setTimeout(() => {
                        this.$refs.dialogSendBySMS.open = true
                        this.secret_to_copy = this.data._id
                    }, 100);
                    break;
            }

            this.selectedMenu = null
        }
    }
})
</script>
<style scoped>
.v-list{
    padding: 0;
}

.v-list-item__content {
    margin-left: 10px;
}

.v-list-item--link:hover {
    background-color: #fccb58;
}
</style>