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
          :workspace="workspace"
          @selectWorkspace="selectWorkspace"
          :owner="workspace.owner === $store.state.user._id"
          :selected="workspace._id === $store.state.selected_workspace._id"
        />
      </div>
    </span>

    <!-- <export-workspace /> -->
    <workspace-delete @workspaceDeleted="fetchWorkspaces" />

  </v-navigation-drawer>
</template>

<script>
import WorkspaceDelete from "./Dialogs/WorkspaceDelete.vue"
// import ExportWorkspace from "./Dialogs/ExportWorkspace.vue"
import { defineComponent } from '@vue/composition-api'
import EditWorkspace from './Forms/EditWorkspace.vue'
import WorkspaceIcon from './WorkspaceIcon.vue'
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
  components: { 
    // ExportWorkspace,
    WorkspaceDelete,
    EditWorkspace,
    WorkspaceIcon,
  },

  data: (vm) => ({
    workspaces: [],
    dialogWorkspaceDelete: false,
    tooltip_copy: false,
    interval: null,
    tooltipWorkspaceId: vm.$t('tooltip.copy_id'),
    workspace_to_edit: null,
    x: 0,
    y: 0
  }),
  
  destroyed() {
    if (this.interval) {
      clearInterval(this.interval)
    }
  },

  mounted() {
    setTimeout(() => {
      this.fetchWorkspaces()
    }, 200);
    EventBus.$on("reloadWorkspaces", () => {
      this.fetchWorkspaces()
    })

    EventBus.$on("importStarted", (workspace_id) => {
      for (const i in this.workspaces) {
        if (this.workspaces[i]._id === workspace_id) {
          this.workspaces[i].import_in_progress = true

          this.interval = setInterval(async () => {
            const uri = `/api/v1/workspace/${workspace_id}`
            const { data } = await http.get(uri)
            if (!data.import_in_progress) {
              this.workspaces[i].import_in_progress = false
              clearInterval(this.interval)

              this.$toast.success("Import successfully ended", {
                closeOnClick: true,
                timeout: 3000,
                icon: true
              })
            }
          }, 5000);
        }
      }
    })

    EventBus.$on("importFinished", (workspace_id) => {
      for (const i in this.workspaces) {
        if (this.workspaces[i]._id == workspace_id) {
          this.workspaces[i].import_in_progress = false
        }
      }
    })
  },

  methods: {
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
  
    async fetchWorkspaces() {
      this.workspaces = []
      
      const response = await http.get("/api/v1/workspace/")
      this.workspaces = response.data

      if (this.workspaces.length === 0) {
        localStorage.removeItem("current_workspace")
      }

      const current_workspace = this.getCurrentWorkspace()
      if (current_workspace) {
        this.selectWorkspace(current_workspace)
      }
    },

    copyWorkspaceID(workspace_id) {
      this.$copyText(workspace_id)

      setTimeout(() => {
        this.tooltipWorkspaceId = this.$t("help.copied")
        this.tooltip_copy = true

        setTimeout(() => {
          this.tooltip_copy = false

          setTimeout(() => {
            this.tooltipWorkspaceId = this.$t("tooltip.copy_id")
          }, 500);
        }, 1000);
      }, 50);
    },
  }
})
</script>