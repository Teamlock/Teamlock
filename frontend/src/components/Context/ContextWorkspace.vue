<template>
    <v-list
        v-if="workspace"
        style="text-align: left"
        class="pt-0 pb-0"
        width="250"
        light
        dense
        tile
    >
        <v-subheader>
            <v-icon style="margin-right: 5px">{{ workspace.icon }}</v-icon>
            <b style="font-size: 15px">{{ workspace.name }}</b>

            <v-spacer />
            <v-tooltip
            v-model="tooltip_copy"
            bottom
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                v-bind="attrs"
                v-on="on"
                @click.stop="copyWorkspaceID(workspace._id)"
                small
                icon
                tile
              >
                <v-icon small>mdi-content-copy</v-icon>
              </v-btn>
            </template>
            <span v-html="tooltipWorkspaceId" />
          </v-tooltip>
          <span v-if="workspace.is_owner">
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
        </v-subheader>

        <v-divider />
        <v-list-item-group color="primary">
            <v-list-item
                v-if="workspace.is_owner"
                @click="editWorkspace()"
            >
                <v-list-item-icon>
                    <v-icon :size="17">mdi-pencil</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                    <v-list-item-title>
                        {{ $t('label.edit_workspace') }}
                    </v-list-item-title>
                </v-list-item-content>
            </v-list-item>
            <v-list-item
                v-if="workspace.is_owner || workspace.can_share"
                @click="shareWorkspace()"
            >
                <v-list-item-icon>
                    <v-icon :size="17">mdi-share</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                    <v-list-item-title>{{ $t('label.share_workspace') }}</v-list-item-title>
                </v-list-item-content>
            </v-list-item>
            <v-list-item
                v-if="workspace.is_owner || workspace.can_write"
                @click="importXML()"
            >
                <v-list-item-icon>
                    <v-icon :size="17">mdi-upload</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                    <v-list-item-title>{{ $t('label.import_workspace') }}</v-list-item-title>
                </v-list-item-content>
            </v-list-item>

            <!-- <v-list-item
                v-if="workspace.is_owner || workspace.can_export"
                @click="exportWorkspace()"
            >
                <v-list-item-icon>
                    <v-icon :size="17">mdi-download</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                    <v-list-item-title>{{ $t('label.export_workspace') }}</v-list-item-title>
                </v-list-item-content>
            </v-list-item> -->

            <span v-if="workspace.is_owner">
                <v-divider />
                <v-list-item
                    @click="deleteWorkspace()"
                >
                    <v-list-item-icon>
                        <v-icon :size="17">mdi-delete</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('label.delete_workspace') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </span>
        </v-list-item-group>
        
    </v-list>
</template>

<script>
import EventBus from "@/event"

export default {
    props: {
        workspace: {
            type: Object,
            required: false
        }
    },

    data: (vm) => ({
        tooltip_copy: false,
        tooltipWorkspaceId: vm.$t('tooltip.copy_id'),
    }),

    methods: {
        editWorkspace() {
            EventBus.$emit("editWorkspace", this.workspace)
        },
        shareWorkspace() {
            EventBus.$emit('shareWorkspace', this.workspace._id)
        },
        importXML() {
            EventBus.$emit('importXML')
        },
        // exportWorkspace() {
        //     EventBus.$emit("exportWorkspace", this.workspace)
        // },
        deleteWorkspace() {
            EventBus.$emit("deleteWorkspace", this.workspace._id)
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
}
</script>

<style scoped>
.v-list{
    padding: 0;
}

.v-list-item__content {
    /* margin-left: 10px; */
}

.v-list-item__icon{
    margin-right: 10px !important;
}

.v-list-item--link:hover {
    background-color: #fccb58;
}
</style>