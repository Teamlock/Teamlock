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
import EventBus from "@/event.js"

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
        is_trash:false,
        in_trash: false,
    }),

    computed:{
        getLabel(){
            if (this.is_trash) return "label.empty_trash";
            return "label.delete_folder";
        },
        getWarning(){
            if (this.is_trash) return "warning.confirm_empty_trash";
            return "warning.confirm_delete_folder";
        }
    },

    mounted() {
        EventBus.$on("folder_trash",res => {
            this.is_trash = res.is_trash;
            this.in_trash = res.in_trash;
        });
    },

    methods: {
         deleteFolder() {
             this.is_loading = true
             if(this.is_trash){
                EventBus.$emit("empty_trash");
                this.open = false;
                this.$emit("folderDeleted", this.parent_id);
                this.is_loading = false
             }else{
                let uri = `/api/v1/folder/${this.folder_id}`;
                let msgKey = "success.folder_deleted"
                if(!this.is_trash && !this.in_trash){
                    uri += "/trash";
                    msgKey = "success.folder_moved_to_trash";
                }
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
             }
        },
    }
})
</script>
