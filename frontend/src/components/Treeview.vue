<template>
    <span>
        <v-card
            :loading="loading"
            class="text-left treeview-card"
            elevation="0"
            @click.right="contextMenuTreeview"
            fill-height
        >
            <sl-vue-tree 
                ref="tree" 
                v-model="folders"
                @drop="dropEnd"
                :allowMultiselect="false"
                @select="selectFolder"
                @nodedblclick="toggleFolder"
                @externaldrop="externalDrop"
                @nodecontextmenu="contextMenuFolder"
            >
                <template slot="title" slot-scope="{ node }">
                    <span class="item-icon">
                        <v-icon v-if="node.data.icon"  :size="17">{{ node.data.icon }}</v-icon>
                        <v-icon v-else :size="17">mdi-folder</v-icon>
                    </span>
                    {{ node.title }}
                </template>
            </sl-vue-tree>
        </v-card>
        <portal to="contextMenuFolder">
            <vue-context ref="menuFolder" v-slot="{ data }" class="p-0">
                <context-folder :node="data" />
            </vue-context>
            <vue-context ref="menuTreeview" class="p-0">
                <context-treeview />
            </vue-context>
        </portal>
    </span>
</template>

<script>
import ContextTreeview from './Context/ContextTreeview.vue';
import { defineComponent } from '@vue/composition-api'
import ContextFolder from './Context/ContextFolder.vue';
import "sl-vue-tree/dist/sl-vue-tree-minimal.css"
import 'vue-context/src/sass/vue-context.scss';
import VueContext from 'vue-context';
import SlVueTree from "sl-vue-tree"
import EventBus from "@/event.js"
import http from "@/utils/http"

export default defineComponent({
    components: {
        ContextTreeview,
        ContextFolder,
        VueContext,
        SlVueTree
    },

    data: () => ({
        selectedFolder: [],
        loading: false,
        folders: []
    }),

    mounted() {
        EventBus.$on("refreshTreeview", () => {
            const selected_folder = localStorage.getItem("selected_folder")
            this.fetchFolders(selected_folder)
        })
    },

    methods: {
        renderCaret(expanded) {
            return expanded ? "fa fa-caret-down" : "fa fa-caret-right"
        },

        findChildren(folders, parent_id, selected_folder) {
            let current_children = []
            let open = false

            for (const folder of folders) {
                if (folder.parent === parent_id) {
                    const { is_open, children } = this.findChildren(folders, folder._id, selected_folder)
                    if (is_open || folder._id === selected_folder) {
                        open = true
                    }

                    current_children.push({
                        id: folder._id,
                        icon: folder.icon,
                        title: folder.name,
                        isLeaf: false,
                        isSelected: folder._id === selected_folder,
                        isExpanded: is_open,
                        data: folder,
                        children: children
                    })
                }
            }

            return { is_open: open, children: current_children }
        },

        construct_tree(folders, selected_folder) {
            let tree = []
            let found = false
            for (let folder of folders) {
                if (!folder.parent) {
                    let { is_open, children } = this.findChildren(folders, folder._id, selected_folder)

                    if (folder._id === selected_folder) {
                        is_open = true
                    }

                    if (is_open) {
                        found = folder
                    }

                    tree.push({
                        id: folder._id,
                        icon: folder.icon,
                        title: folder.name,
                        isLeaf: false,
                        isExpanded: is_open,
                        isSelected: folder._id === selected_folder,
                        data: folder,
                        children: children
                    })
                }
            }

            if (!found) {
                if (tree.length > 0) {
                    tree[0].isExpanded = true
                    tree[0].isSelected = true
                    this.$store.dispatch("set_current_folder", tree[0].data._id)
                    EventBus.$emit("selectedFolder", {
                        _id: tree[0].data._id,
                        name: tree[0].data.name,
                        icon: tree[0].data.icon,
                    })
                }
            } else {
                this.$store.dispatch("set_current_folder", selected_folder)
                EventBus.$emit("selectedFolder", {
                    _id: found._id,
                    name: found.name,
                    icon: found.icon
                })
            }

            return tree
        },

        fetchFolders(selected_folder) {
            let workspace_id = this.$store.state.selected_workspace._id
            if (workspace_id) {
                this.loading = true 
                this.folders = []

                http.get(`/api/v1/workspace/${workspace_id}/folders`)
                    .then((response) => {

                        if (!selected_folder) {
                            selected_folder = localStorage.getItem("selected_folder")
                        }

                        this.folders = this.construct_tree(response.data, selected_folder)
                        this.loading = false
                    })
            }
        },

        selectFolder(selected) {
            const folder_id = selected[0].data._id
            EventBus.$emit("selectedFolder", {
                _id: selected[0].data._id,
                name: selected[0].data.name,
                icon: selected[0].data.icon,
            })
            EventBus.$emit("showTrash",false)
            localStorage.setItem("showTrash", false)
            
            localStorage.setItem("selected_folder", folder_id)
            this.$store.dispatch("set_current_folder", folder_id)
        },

        toggleFolder(selected) {
            const node = this.$refs.tree.getNode(selected.path)
            this.$refs.tree.updateNode(selected.path, {isExpanded: !node.isExpanded})
        },

        contextMenuFolder(node, e) {
            e.preventDefault() 
            e.stopPropagation()
            this.$refs.tree.select(node.path)
            this.$refs.menuTreeview.close()
            this.$refs.menuFolder.open(e, node)
        },

        contextMenuTreeview(e) {
            e.preventDefault()
            this.$refs.menuFolder.close()
            this.$refs.menuTreeview.open(e)
        },

        dropEnd(node_dragged, node_dest) {
            const folder_to_move = node_dragged[0].data

            this.loading = true
            let folder_dest = node_dest.node.data

            if (node_dest.placement !== "inside") {
                folder_dest = node_dest.node.data
                if (!folder_dest.parent) {
                    folder_dest._id = null
                    folder_to_move.moved = true
                }
            }

            folder_to_move.parent = folder_dest._id

            const uri = `/api/v1/folder/${folder_to_move._id}`
            http.put(uri, folder_to_move).then(() => {
                this.$toast.success(`Folder ${folder_to_move.name} successfully updated`, {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
                this.fetchFolders(folder_to_move._id)
            }).then(() => {
                this.loading = false;
            })
        },

        externalDrop(cursor) {
            // Check if a key is being dropped
            const secret_id = sessionStorage.getItem("draggedKey")
            if (secret_id) {
                const to_node = cursor.node
                const folder_id = to_node.data._id

                const uri = `/api/v1/secret/${secret_id}/move`
                http.post(uri, folder_id).then(() => {
                    this.$toast.success(this.$t("success.key_moved"), {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })
                    this.fetchFolders(folder_id)
                })
            }
        }
    }
})
</script>

<style>
.sl-vue-tree-node-item{
    padding-left: 5px;
}

.sl-vue-tree-title{
    font-size: 14px;
}

.item-icon{
    font-size: 12px;
}

.sl-vue-tree-selected > .sl-vue-tree-node-item{
    background-color: transparent !important;
    /* color: rgb(41, 41, 41); */
}

.v-context {
    padding: 0 !important;
}
</style>