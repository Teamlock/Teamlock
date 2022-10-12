<template>
    <div>
        <v-list dense v-if="node" style="text-align: left" light>
            <v-subheader>
                <v-icon style="margin-right: 5px" v-if="node.data.icon">{{ node.data.icon }}</v-icon>
                <v-icon style="margin-right: 5px" v-else>mdi-folder</v-icon>
                <b style="font-size: 15px">{{ node.data.name }}</b>
            </v-subheader>
            <v-divider />
            <v-list-item-group color="primary" v-model="selectedMenu">
                <v-list-item v-if="!in_trash && !is_trash">
                    <v-list-item-icon class="mr-2">
                        <v-icon :size="17">mdi-pencil</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('folder.edit') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="!in_trash && !is_trash">
                    <v-list-item-icon class="mr-2">
                        <v-icon :size="17">mdi-plus</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('folder.add') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
                <v-divider />
                <v-list-item v-if="!in_trash && !is_trash">
                    <v-list-item-icon class="mr-2">
                        <v-icon :size="17">mdi-content-copy</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('folder.copy') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
                <v-divider />
                <v-list-item>
                    <v-list-item-icon class="mr-2">
                        <v-icon :size="17">mdi-delete</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title v-if="is_trash">{{ $t('label.empty_trash') }}</v-list-item-title>
                        <v-list-item-title v-else>{{ $t('label.delete') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list-item-group>
        </v-list>
        
        <folder-delete
            ref="dialogDeleteFolder"
            :folder_id="folder_to_delete"
            :parent_id="parent_id"
            @folderDeleted="folderDeleted"
        />

        <copy-folder-dialog 
            ref="dialogCopyFolder"
            :folder_id="folder_to_copy"
            @folderCopied="folderCopied"
        />
    </div>
</template>

<script>
import CopyFolderDialog from '../Dialogs/CopyFolderDialog.vue'
import { defineComponent } from '@vue/composition-api'
import FolderDelete from '../Dialogs/FolderDelete.vue'
import EventBus from "@/event"

export default defineComponent({
  components: { FolderDelete, CopyFolderDialog },
    props: {
        node: {
            type: Object,
            required: false
        }
    },

    data: () => ({
        dialogConfirmDeleteFolder: false,
        folder_to_delete: null,
        parent_id: null,
        folder_to_copy: null,
        selectedMenu: null,
        is_trash:false,
        in_trash:false
    }),

    mounted(){
        EventBus.$on("folder_trash",res =>{
            this.is_trash = res.is_trash;
            this.in_trash = res.in_trash;
        })
    },  

    watch: {
        selectedMenu(val) {
            if (val === null) {
                return
            }
            if(this.in_trash || this.is_trash){
                this.$refs.dialogDeleteFolder.open = true
                this.folder_to_delete = this.node.data._id
                this.parent_id = this.node.data.parent
            }else{
                switch(val) {
                    case 0:
                        this.editFolder()
                        break;
                    case 1:
                        this.addFolder()
                        break;
                    case 2:
                        this.$refs.dialogCopyFolder.open = true
                        this.folder_to_copy = this.node.data._id
                        this.$refs.dialogCopyFolder.fetchWorkspaces()
                        break;
                    case 3:
                        this.$refs.dialogDeleteFolder.open = true
                        this.folder_to_delete = this.node.data._id
                        this.parent_id = this.node.data.parent
                        break;
                }
            }
            this.selectedMenu = null
        }
    },

    methods: {
        editFolder() {
            EventBus.$emit("editFolder", this.node.data._id)
        },
        addFolder() {
            EventBus.$emit("editFolder", null, this.node.data._id)
        },
        folderDeleted(parent_id) {
            this.folder_to_delete = null
            EventBus.$emit('refreshTreeview', parent_id)
        },
        folderCopied() {
            this.folder_to_copy = null
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