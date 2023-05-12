<template>
    <v-dialog v-model="open" width="60%" persistent>
        <v-card v-if="workspace_id" :loading="isLoading">
            <v-app-bar flat dense class="edit_workspace_bar">
                <v-app-bar-nav-icon>
                    <v-icon>mdi-share</v-icon>
                </v-app-bar-nav-icon>

                <v-toolbar-title class="pl-0">
                    {{$t('title.share_workspace')}}
                </v-toolbar-title>
                <v-spacer />
                <v-btn x-small text @click="close()">
                    <v-icon small>mdi-close-thick</v-icon>
                </v-btn>
            </v-app-bar>

            <v-card-text class="no-padding">
                <v-data-table
                    :headers="headers"
                    :items="users"
                    :items-per-page="10"
                    sort-by="user_email"
                    :sort-desc="false"
                    :footer-props="{'items-per-page-options':[10, 20, 50, 100]}"
                >
                    <template v-slot:[`header._id`]="{}">
                        <v-menu
                            :close-on-content-click="false"
                            :close-on-click="false"
                            @close="$refs.addUserShare.emptyForm()"
                            v-model="menuAddUser"
                            bottom
                            offset-y
                            max-width="1000"
                            left
                        >
                            <template v-slot:activator="{ on, attrs }">
                                <v-btn x-small color="primary" v-on="on" v-bind="attrs" style="float: right">
                                    <v-icon small>mdi-plus</v-icon>
                                    {{ $t("button.add_user") }}
                                </v-btn>
                            </template>
                            <add-user-share
                                ref="addUserShare"
                                :selectedWorkspace="workspace_id"
                                @close="menuAddUser = false"
                                @reload="getUsers()"
                            />
                        </v-menu>
                    </template>

                    <template v-slot:[`item.is_owner`]="{ item }">
                        <v-switch
                            class="mt-0"
                            hide-details
                            :disabled="item.is_owner"
                            v-model="item.is_owner"
                            @change="changeOwner(item)"
                        />
                    </template>

                    <template v-slot:[`item.can_read`]="{}">
                        <v-icon color="green">mdi-check</v-icon>
                    </template>

                    <template v-slot:[`item.can_write`]="{ item }">
                        <v-switch
                            class="mt-0"
                            hide-details
                            v-model="item.can_write"
                            @change="rightChange(item)"
                        />
                    </template>

                    <template v-slot:[`item.can_share`]="{ item }">
                        <v-switch
                            class="mt-0"
                            hide-details
                            v-model="item.can_share"
                            @change="rightChange(item)"
                        />
                    </template>

                    <template v-slot:[`item.can_export`]="{ item }">
                        <v-switch
                            class="mt-0"
                            hide-details
                            v-model="item.can_export"
                            @change="rightChange(item)"
                        />
                    </template>

                    <template v-slot:[`item.can_share_external`]="{ item }">
                        <v-switch
                            class="mt-0"
                            hide-details
                            v-model="item.can_share_external"
                            @change="rightChange(item)"
                        />
                    </template>

                    <template v-slot:[`item.expire_at`]="{ item }">
                        <span v-html="renderDate(item.expire_at, 'DD/MM/YYYY')"/>
                    </template>

                    <template v-slot:[`item._id`]="{ item }">
                        <v-menu offset-x>
                            <template v-slot:activator="{ on, attrs }">
                                <v-icon v-bind="attrs" v-on="on">
                                    mdi-delete
                                </v-icon>
                            </template>
                            <v-card>
                                <v-card-title style="font-size: 16px">
                                    <v-icon>mdi-trash</v-icon>
                                    &nbsp;{{ $t('warning.confirm_share_delete') }}
                                </v-card-title>
                                <v-card-actions>
                                    <v-spacer />
                                    <v-btn small text>{{ $t('button.cancel') }}</v-btn>
                                    <v-btn small text color="primary" @click="deleteShare(item._id)">{{ $t('button.confirm') }}</v-btn>
                                </v-card-actions>
                            </v-card>
                        </v-menu>
                    </template>
                </v-data-table>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import addUserShare from '../Forms/addUserShare.vue'
import renderMixin from "@/mixins/render"
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
  mixins: [renderMixin],
  components: { addUserShare },
    data: () => ({
        menuAddUser: false,
        workspace_id: null,
        isLoading: false,
        is_pro: false,
        open: false,
        search:'',
        headers: [],
        switch: false,
        users: []
    }),

    watch: {
        open(val) {
            if (!val) {
                this.users = []
            }
        },

        menuAddUser(val) {
            if (val) {
                setTimeout(() => {
                    this.$refs.addUserShare.getUsers()
                }, 200);
            }
        }
    },

    async beforeMount() {
        this.is_pro = this.$store.state.pro
    },

    mounted() {
        EventBus.$on("shareWorkspace", async (workspace_id) => {
            this.workspace_id = workspace_id
            await this.getWorkspace()
            this.getUsers()
            this.open = true;
        })
    },

    destroyed() {
        this.close()
    },

    methods: {
        constructHeaders(isOwner) {
            let headers = [
                {text: this.$t("label.email"), align: 'start', sortable: true, value: 'user_email'}
            ]
            if (isOwner) {
                headers.push({text: this.$t('label.is_owner'), value:"is_owner", visible: this.isOwner})
            }

            headers.push(...[
                {text: this.$t('label.can_read'), value:"can_read"},
                {text: this.$t('label.can_write'), value:"can_write"},
                {text: this.$t('label.can_share'), value:"can_share"},
                {text: this.$t('label.can_export'), value:"can_export"}
            ])

            if (this.is_pro) {
                headers.push({text: this.$t('label.can_share_external'), value:"can_share_external"})
            }

            headers.push({text: this.$t('label.expire'), value:"expire_at"})
            headers.push({text: "", value:"_id", sortable: false})
            this.headers = headers
        },

        async getWorkspace() {
            const { data } = await http.get(`/api/v1/workspace/${this.workspace_id}`)
            this.constructHeaders(data.is_owner)
        },

        close() {
            try {
                this.$refs.addUserShare.emptyForm();
                this.users = []
            } catch(err) {
                // Continue
            }
            this.open = false
            EventBus.$emit("reloadWorkspaces")
        },

        getUsers() {
            const uri = `/api/v1/workspace/${this.workspace_id}/share`
            http.get(uri).then((response) => {
                this.users = response.data
            })
        },

        deleteShare(share_id) {
            this.isLoading = true
            const uri = `/api/v1/workspace/${this.workspace_id}/share/${share_id}`
            http.delete(uri).then(() => {
                this.$toast.success(this.$t("success.users_removed_from_workspace"))

                this.isLoading = false
                this.getUsers()
                this.$refs.addUserShare.getUsers()
            })
        },

        rightChange(share) {
            const form = {
                can_write: share.can_write,
                can_share: share.can_share,
                can_export: share.can_export,
                can_share_external: share.can_share_external
            }

            const uri = `/api/v1/workspace/${this.workspace_id}/share/${share._id}`
            http.put(uri, form).then(() => {
                this.$toast.success(this.$t('success.shared_updated'))
                this.getUsers()
            })
        },

        changeOwner(share) {
            const form = {
                new_user: share.user
            }

            const uri = `/api/v1/workspace/${this.workspace_id}/owner`
            http.put(uri, form).then(() => {
                this.$toast.success(this.$t("Ownership successfully changed"))
                this.getWorkspace()
                this.getUsers()
            })
        }
    },
})
</script>
