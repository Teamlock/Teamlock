<template>
  <v-navigation-drawer
    style="padding-top: 100px; z-index: 0"
    :width="60"
    permanent
    absolute
  >
    <template v-slot:append>
      <edit-workspace @refresh="fetchWorkspaces" />
    </template>
    <span v-if="$store.state.selected_workspace && $store.state.user">
      <div v-for="workspace in workspaces" :key="workspace._id">
        <workspace-icon
          @showMenu="show"
          @selectWorkspace="selectWorkspace"
          :workspace="workspace"
          :owner="workspace.owner === $store.state.user._id"
          :selected="workspace._id === $store.state.selected_workspace._id"
        />
      </div>
    </span>

    <v-menu
      v-model="showMenu"
      v-if="workspace_to_edit"
      :position-x="x"
      :position-y="y"
      absolute
      offset-x
    >
      <v-card class="mx-auto text-left" width="300" flat>
        <v-app-bar flat dense class="edit_workspace_bar">
          <v-app-bar-nav-icon v-if="workspace_to_edit.icon">
            <v-icon>{{ workspace_to_edit.icon }}</v-icon>
          </v-app-bar-nav-icon>
          <v-toolbar-title class="pl-0">
            {{ workspace_to_edit.name }}
          </v-toolbar-title>

          <v-spacer />
          <v-tooltip
            v-model="tooltip_copy"
            bottom
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                v-bind="attrs"
                v-on="on"
                @click.stop="copyWorkspaceID(workspace_to_edit._id)"
                small
                icon
                tile
              >
                <v-icon small>mdi-content-copy</v-icon>
              </v-btn>
            </template>
            <span v-html="tooltipWorkspaceId" />
          </v-tooltip>
          <span v-if="workspace_to_edit.owner === $store.state.user._id">
            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-btn
                  v-on="on"
                  v-bind="attrs"
                  icon
                  tile
                  small
                >
                  <v-icon
                    style="float: right"
                    color="primary"
                    small
                  >
                    mdi-star
                  </v-icon>
                </v-btn>
              </template>
              <span>{{ $t("label.workspace_owner") }}</span>
            </v-tooltip>
          </span>
        </v-app-bar>
        <v-card-text>
          <v-row dense>
            <v-col v-if="workspace_to_edit.owner === $store.state.user._id">
              <edit-workspace-button :workspace="workspace_to_edit" />
            </v-col>
            <v-col v-if="workspace_to_edit.owner === $store.state.user._id || workspace_to_edit.can_share">
              <share-button :workspace="workspace_to_edit" />
            </v-col>
          </v-row>

          <v-row dense>
            <v-col v-if="workspace_to_edit.owner === $store.state.user._id || workspace_to_edit.can_write">
              <import-button :workspace="workspace_to_edit" />
            </v-col>
            <v-col v-if="workspace_to_edit.owner === $store.state.user._id">
              <delete-button :workspace="workspace_to_edit" />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-menu>

    <workspace-delete @workspaceDeleted="fetchWorkspaces" />

  </v-navigation-drawer>
</template>

<script>
import EditWorkspaceButton from "./Buttons/EditWorkspaceButton.vue"
import WorkspaceDelete from "./Dialogs/WorkspaceDelete.vue"
import { defineComponent } from '@vue/composition-api'
import EditWorkspace from './Forms/EditWorkspace.vue'
import ImportButton from './Buttons/ImportButton.vue'
import DeleteButton from './Buttons/DeleteButton.vue'
import ShareButton from "./Buttons/ShareButton.vue"
import WorkspaceIcon from './WorkspaceIcon.vue'
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
  components: { 
    EditWorkspaceButton,
    WorkspaceDelete,
    EditWorkspace,
    WorkspaceIcon,
    ImportButton,
    DeleteButton,
    ShareButton,
  },

  data: (vm) => ({
    workspaces: [],
    workspace_edit: null,
    workspaceEditOpen: false,
    dialogWorkspaceDelete: false,
    tooltip_copy: false,
    showMenu: false,
    tooltipWorkspaceId: vm.$t('help.tooltip_workspace_id'),
    workspace_to_edit: null,
    x: 0,
    y: 0
  }),

  mounted() {
    setTimeout(() => {
      this.fetchWorkspaces()
    }, 200);
    EventBus.$on("reloadWorkspaces", () => {
      this.fetchWorkspaces()
    })
  },

  methods: {
    show (e, workspace) {
      e.preventDefault()
      this.workspace_to_edit = workspace
      this.showMenu = false
      this.x = e.clientX
      this.y = e.clientY
      this.$nextTick(() => {
        this.showMenu = true
      })
    },

    selectWorkspace(workspace_id, manual) {
      if (manual ){
        localStorage.removeItem("selected_folder")
        localStorage.setItem("current_workspace", workspace_id)
      }

      this.$store.commit("SET_WORKSPACE", workspace_id)
    },

    confirmDeleted() {
      this.dialogWorkspaceDelete = false
      this.fetchWorkspaces()
    },

    getCurrentWorkspace() {
      const current_workspace = localStorage.getItem("current_workspace")

      if (this.workspaces.length > 0) {
        let found = false
        for (const wp of this.workspaces) {
          if (wp._id === current_workspace) {
            found = true
          }
        }

        if (!found) {
          localStorage.removeItem("curent_workspace")
        }

        if (current_workspace && found) {
          return current_workspace
        } else {
          return this.workspaces[0]._id
        }
      } else {
        localStorage.removeItem("current_workspace")
        return this.workspaces[0]._id
      }
    },
  
    fetchWorkspaces() {
      this.workspaces = []

      http.get("/api/v1/workspace/")
        .then((response) => {
          this.workspaces = response.data

          if (this.workspaces.length === 0) {
            localStorage.removeItem("current_workspace")
          }

          const current_workspace = this.getCurrentWorkspace()
          if (current_workspace) {
            this.selectWorkspace(current_workspace)
          }
        })
    },

    copyWorkspaceID(workspace_id) {
      this.$copyText(workspace_id)

      setTimeout(() => {
        this.tooltipWorkspaceId = this.$t("help.copied")
        this.tooltip_copy = true

        setTimeout(() => {
          this.tooltip_copy = false

          setTimeout(() => {
            this.tooltipWorkspaceId = this.$t("help.tooltip_workspace_id")
          }, 500);
        }, 1000);
      }, 50);
    },
  }
})
</script>