<template>
    <v-container fluid>
        <v-row class="v_row_user">
            <v-col md="3">
                <v-card class="text-left vcard_dashboard_user" elevation="1">
                    <v-list-item three-line>
                        <v-list-item-avatar
                            color="rgba(218, 171, 57,0.3)"
                            dark
                            size="50"
                            class="ml-3"
                        >
                            <v-icon color="#daab39" size="30">mdi-account-group</v-icon>
                        </v-list-item-avatar>

                        <v-list-item-content>
                            <div class="text-overline title_dashboard_user">
                                {{ $t("label.total_users") }}
                            </div>
                            <v-list-item-title class="text-h4 mb-1 count_dashboard_user">
                                {{ totalUsers }}
                            </v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                </v-card>
            </v-col>
            
            <v-col md="3">
                <v-card class="text-left vcard_dashboard_user" elevation="1">
                    <v-list-item three-line>
                        <v-list-item-avatar
                            dark
                            size="50"
                            class="ml-3"
                            color="rgba(218, 171, 57,0.3)"
                        >
                            <v-icon dark color="#daab39" size="30">mdi-crown-outline</v-icon>
                        </v-list-item-avatar>
                            <v-list-item-content>
                                <div class="text-overline mb-1 title_dashboard_user">
                                    {{ $t("label.total_admin_users") }}
                                </div>
                                <v-list-item-title class="text-h4 mb-1 title_dashboard_user">
                                    {{ totalAdminUsers }}
                                </v-list-item-title>
                            </v-list-item-content>
                        </v-list-item>
                </v-card>
            </v-col>
            <v-col md="3">
                <v-card class="text-left vcard_dashboard_user" elevation="1">
                    <v-list-item three-line>
                        <v-list-item-avatar
                            color="rgba(218, 171, 57,0.3)"
                            dark
                            size="50"
                            class="ml-3"
                        >
                            <v-icon color="#daab39" size="30">mdi-cog</v-icon>
                        </v-list-item-avatar>

                        <v-list-item-content>
                            <div class="text-overline mb-1 title_dashboard_user">
                                {{ $t("label.total_not_configured_users") }}
                            </div>
                            <v-list-item-title class="text-h4 mb-1 title_dashboard_user">
                                {{ totalNotConfiguredUsers }}
                            </v-list-item-title>
                        </v-list-item-content>

                    </v-list-item>
                </v-card>
            </v-col>
            <v-col md="3">
                <v-card class="text-left vcard_dashboard_user" elevation="1">
                    <v-list-item three-line>
                    <v-list-item-avatar
                        color="rgba(255,0,0,0.3)"
                        dark
                        size="50"
                        class="ml-3"
                    >
                        <v-icon color="error" size="30">mdi-lock-remove</v-icon>
                    </v-list-item-avatar>
                        <v-list-item-content>
                            <div class="text-overline mb-1 title_dashboard_user">
                                {{ $t("label.total_locked_users") }}
                            </div>
                            <v-list-item-title class="text-h4 mb-1 title_dashboard_user">
                                {{ totalLockedUsers }}
                            </v-list-item-title>
                        </v-list-item-content>

                    </v-list-item>
                </v-card>
            </v-col>
        </v-row>
        <v-row>
            <v-col>
                <v-data-table
                    dense
                    :headers="headersUsers"
                    :items="users"
                    :items-per-page="20"
                    :options.sync="options"
                    :server-items-length="totalUsers"
                    :sort-by="sortBy"
                    :sort-desc="sortDesc"
                    :loading="loading"
                    class="elevation-2"
                    :footer-props="{'items-per-page-options':[5, 10, 20, 50, 100]}"
                >
                    <template v-slot:top>
                        <v-toolbar dense flat>
                            <v-toolbar-title>
                                <v-icon>mdi-account-group</v-icon>
                                {{ $t('label.users') }}
                            </v-toolbar-title>
                            <v-divider
                                class="mx-4"
                                inset
                                vertical
                            />
                            <v-text-field
                                v-model="search"
                                append-icon="mdi-magnify"
                                @keyup.enter="getUsers()"
                                :label="$t('label.search')"
                                style="width: 100px"
                                hide-details
                            />
                            <v-spacer />
                            <v-switch class="mt-5 mr-5" v-model="adminUsers" :label="$t('label.admin_users')"/>
                            <v-switch class="mt-5 mr-5" v-model="lockedUsers" :label="$t('label.locked_users')"/>
                            <v-switch class="mt-5" v-model="notConfiguredUsers" :label="$t('label.not_configured_users')"/>
                            <v-divider
                                class="mx-4"
                                inset
                                vertical
                            />

                            <v-tooltip bottom>
                                <template v-slot:activator="{ on, attrs }">
                                    <v-btn
                                        @click="addUserDialog = true"
                                        class="elevation-1 mr-2"
                                        color="#daaf39"
                                        v-bind="attrs"
                                        v-on="on"
                                        small
                                        tile
                                        dark
                                    >
                                        <v-icon>mdi-plus</v-icon>
                                    </v-btn>
                                </template>
                                <span>{{ $t("help.add_user") }}</span>
                            </v-tooltip>

                            <v-tooltip bottom>
                                <template v-slot:activator="{ on, attrs }">
                                    <v-btn
                                        @click="importUserDialog = true"
                                        color="#daaf39"
                                        class="elevation-1"
                                        v-bind="attrs"
                                        v-on="on"
                                        tile
                                        small
                                        dark
                                    >
                                        <v-icon>mdi-upload</v-icon>
                                    </v-btn>
                                </template>
                                <span>{{ $t("help.bulk_import_user") }}</span>
                            </v-tooltip>
                        </v-toolbar>
                    </template>
                    <template v-slot:[`item.email`]="{ item }">
                        <span v-html="item.email" />
                    </template>
                    <template v-slot:[`item.last_seen`]="{ item }">
                        <span v-if="item.last_seen" v-html="renderDate(item.last_seen)" />
                        <v-icon v-else small>mdi-block-helper</v-icon>
                    </template>
                    <template v-slot:[`item.otp.enabled`]="{ item }">
                        <v-icon
                            v-html="item.otp.enabled ? 'mdi-check-bold' : 'mdi-close-thick'"
                        />
                    </template>
                    <template v-slot:[`item.is_configured`]="{ item }">
                        <v-icon
                            v-html="item.is_configured ? 'mdi-check-bold' : 'mdi-close-thick'"
                        />
                    </template>
                    <template v-slot:[`item.is_locked`]="{ item }">
                        <v-switch
                            class="mt-0"
                            hide-details
                            v-model="item.is_locked"
                            @change="lockUnlockUser(item)"
                        />
                    </template>
                    <template v-slot:[`item.is_admin`]="{ item }">
                        <v-switch
                            class="mt-0"
                            hide-details
                            v-model="item.is_admin"
                            @change="adminUnAdminUser(item)"
                        />
                    </template>
                    <template v-slot:[`item.recovery_enabled`]="{ item }">
                        <v-switch
                            class="mt-0"
                            hide-details
                            v-model="item.recovery_enabled"
                            @change="enableDisableRecoveryMode(item)"
                        />
                    </template>
                    <template v-slot:[`item._id`]="{ item }">
                        <v-menu offset-y>
                            <template v-slot:activator="{ on: menu, attrs }">
                                <v-tooltip bottom>
                                    <template v-slot:activator="{ on: tooltip }">
                                        <v-icon
                                            v-bind="attrs"
                                            v-on="{ ...tooltip, ...menu }"
                                        >
                                            mdi-delete
                                        </v-icon>
                                    </template>
                                    <span>{{ $t("help.delete_user") }}</span>
                                </v-tooltip>
                            </template>
                            <v-card>
                                <v-card-title style="font-size: 16px">
                                    <v-icon>mdi-delete</v-icon>
                                    &nbsp;<span class="text-body-2">{{ $t('warning.confirm_user_delete') }}</span>
                                </v-card-title>
                                <v-card-actions>
                                    <v-spacer />
                                    <v-btn small text>{{ $t('button.cancel') }}</v-btn>
                                    <v-btn small color="primary" text @click="deleteUser(item)">{{ $t('button.confirm') }}</v-btn>
                                </v-card-actions>
                            </v-card>
                        </v-menu>
                    </template>
                </v-data-table>
            </v-col>
        </v-row>

        <v-dialog v-model="addUserDialog" width="500">
            <add-user @close="refresh" @reload="refresh"/>
        </v-dialog>
        <v-dialog v-model="importUserDialog" width="900">
            <import-users @close="refresh" @reload="refresh"/>
        </v-dialog>
    </v-container>
</template>

<script>
import ImportUsers from '../../components/Forms/ImportUsers.vue'
import AddUser from '../../components/Forms/AddUser.vue'
import { defineComponent } from '@vue/composition-api'
import renderMixin from "@/mixins/render"
import http from "@/utils/http"

export default defineComponent({
    components: { AddUser, ImportUsers },
    mixins: [renderMixin],
    data: () => ({
        headersUsers: [],
        options: {},
        search: "",
        addUserDialog: false,
        importUserDialog: false,
        sortBy: 'email',
        sortDesc: false,
        loading: false,
        totalUsers: 0,
        totalAdminUsers: 0,
        totalNotConfiguredUsers: 0,
        totalLockedUsers: 0,
        users: [],
        adminUsers: false,
        lockedUsers: false,
        notConfiguredUsers: false
    }),

    watch: {
        options: {
            handler () {
                this.getUsers()
            },
            deep: true
        },

        adminUsers() {
            this.getUsers()
        },

        lockedUsers() {
            this.getUsers()
        },

        notConfiguredUsers() {
            this.getUsers()
        }
    },

    beforeMount() {
        this.headersUsers = [
            { text: this.$t("label.email"), value: "email", width: "30%"},
            { text: this.$t("label.last_seen"), value: "last_seen", width: "15%" }
        ]

        this.is_pro = this.$store.state.pro
        if (this.is_pro) {
            this.headersUsers.push({ text: this.$t("label.otp"), value: "otp.enabled", width: "10%" })
        }

        this.headersUsers.push({ text: this.$t("label.configured"), value: "is_configured", width: "10%" })
        this.headersUsers.push({ text: this.$t("label.locked"), value: "is_locked", width: "10%" })
        this.headersUsers.push({ text: this.$t("label.admin_rights"), value: "is_admin", width: "10%" })
        this.headersUsers.push({ text: this.$t("label.recovery"), value: "recovery_enabled", width: "10%" })
        this.headersUsers.push({ text: this.$t("label.actions"), value: "_id", width: "5%"})
    },

    methods: {
        adminUnAdminUser(user) {
            this.loading = true
            const uri = `/api/v1/user/${user._id}`

            http.put(uri, {is_admin: user.is_admin}).then(() => {
                this.$toast.success(this.$t("success.user_updated"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
                this.getUsers()
            })
        },

        enableDisableRecoveryMode(user) {
            this.loading = true
            const uri = `/api/v1/user/recover/${user._id}`

            http.post(uri, {enabled: user.recovery_enabled}).then(() => {
                this.$toast.success(this.$t("success.user_updated"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
                this.getUsers()
            })
        },

        lockUnlockUser(user) {
            this.loading = true
            const uri = `/api/v1/user/lock/${user._id}`

            http.post(uri, {is_locked: user.is_locked}).then(() => {
                this.$toast.success(this.$t("success.user_updated"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
                this.getUsers()
            })
        },

        getUsers() {
            const sort_order = this.options.sortDesc[0] ? "desc" : "asc"
            const params = {
                lockedUsers: this.lockedUsers,
                adminUsers: this.adminUsers,
                notConfiguredUsers: this.notConfiguredUsers ,
                search: this.search,
                page: this.options.page,
                per_page: this.options.itemsPerPage,
                sort: `${this.options.sortBy[0]}|${sort_order}`
            }

            if (!this.options.sortBy[0]) {
                delete params.sort
            }

            this.loading = true
            http.get("/api/v1/user/", { params: params })
                .then((response) => {
                    this.totalUsers = response.data.total
                    this.totalNotConfiguredUsers = response.data.total_not_configured_users
                    this.totalLockedUsers = response.data.total_locked_users
                    this.totalAdminUsers = response.data.total_admin_users
                    this.users = response.data.data
                }).then(() => {
                    this.loading = false
                })
        },

        refresh() {
            this.importUserDialog = false
            this.addUserDialog = false
            this.getUsers()
        },

        deleteUser(user) {
            const uri = `/api/v1/user/${user._id}`
            http.delete(uri).then(() => {
                this.$toast.success(this.$t("success.user_deleted"), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
                this.getUsers()
            })
        }
    }
})
</script>
