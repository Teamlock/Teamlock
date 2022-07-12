<template>
    <div>
        <v-list dense v-if="data" style="text-align: left" color="primary">
            <v-subheader>
                <v-icon style="margin-right: 5px">mdi-key</v-icon>
                <strong style="font-size: 15px">{{ data.name.value }}</strong>
            </v-subheader>
            <v-divider />
            <v-list-item-group color="primary" v-model="selectedMenu">
                <v-list-item>
                    <v-list-item-icon class="mr-2">
                        <v-icon :size="17">mdi-email-fast</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('label.send_by_mail') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="sms">
                    <v-list-item-icon class="mr-2">
                        <v-icon :size="17">mdi-message-processing</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('label.send_by_sms') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list-item-group>
        </v-list>

        <send-by-mail-vue
            ref="dialogSendByMail"
            :key_id="key_to_copy"
        />
        <send-by-sms-vue
            ref="dialogSendBySMS"
            :key_id="key_to_copy"
        />
    </div>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import SendByMailVue from '../Dialogs/SendByMail.vue'
import SendBySmsVue from '../Dialogs/SendBySMS.vue'

export default defineComponent({
    components: { 
        SendByMailVue,
        SendBySmsVue
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
        key_to_copy: null
    }),

    watch: {
        selectedMenu(val) {
            if (val === null) {
                return
            }

            switch(val) {
                case 0:
                    this.$refs.dialogSendByMail.open = true
                    this.key_to_copy = this.data._id
                    break;
                case 1:
                    this.$refs.dialogSendBySMS.open = true
                    this.key_to_copy = this.data._id
                    break;
            }
            this.selectedMenu = null
        }
    },

    methods: {
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
    color: #fff !important;
}
</style>