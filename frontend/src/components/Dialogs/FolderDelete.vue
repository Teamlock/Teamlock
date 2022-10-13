<template>
    <v-dialog
        :loading="is_loading"
        max-width="400"
        v-model="open"
        persistent
    >
        <v-card>
            <v-card-title class="text-h5">
                {{ $t(getLabel) }}
            </v-card-title>
            <v-card-text>{{ $t(getWarning) }}</v-card-text>
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
                @click="deleteFolder"
                :loading="is_loading"
                color="primary"
                small
                text
            >
                {{ $t('button.confirm') }}
            </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import http from "@/utils/http"

export default defineComponent({
    props: {
        folder_id: {
            type: String,
            required: false
        },
        parent_id: {
            type: String,
            required: false
        }
    },

    data: () => ({
        is_loading: false,
        open: false,
    }),

    computed:{
        getLabel(){
            return "label.delete_folder";
        },
        getWarning(){
            return "warning.confirm_delete_folder";
        }
    },

    methods: {
        deleteFolder() {
            this.is_loading = true
            let uri = `/api/v1/folder/${this.folder_id}/trash`;
            let msgKey = "success.folder_deleted"
            http.delete(uri).then(() => {
                    this.$toast.success(this.$t(msgKey), {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })
                    this.open = false
                    this.$emit("folderDeleted", this.parent_id)
                }).then(() => {
                    this.is_loading = false
                })
        },
    }
})
</script>
