<template>
    <v-data-table
        dense
        :headers="headersHistory"
        :items="items"
        :items-per-page="20"
        :options.sync="options"
        :server-items-length="totalLine"
        :sort-by="sortBy"
        :sort-desc="sortDesc"
        :loading="loading"
        class="elevation-2"
        :footer-props="{'items-per-page-options':[5, 10, 20, 50, 100]}"
    >
        <template v-slot:top>
            <v-toolbar flat>
                <v-row>
                    <v-spacer />
                    <v-col :md="3">
                        <v-select
                            prepend-icon="mdi-account"
                            v-model="selectedUsers"
                            :label="$t('label.users')"
                            :items="users"
                            hide-details
                            multiple
                            attach
                        >
                            <template v-slot:selection="{ item, index }">
                                <v-chip small label color="primary" v-if="index < 2">
                                    <span>{{ item }}</span>
                                </v-chip>
                                <span
                                    v-if="index === 2"
                                    class="grey--text text-caption"
                                >
                                    +{{ selectedUsers.length - 2 }} {{ $t('label.others')}}
                                </span>
                            </template>
                        </v-select>
                    </v-col>
                    <v-col :md="3">
                        <v-select
                            prepend-icon="mdi-view-dashboard"
                            v-model="selectedWorkspaces"
                            :label="$t('label.workspaces')"
                            :items="workspaces"
                            hide-details
                            multiple
                            attach
                        >
                            <template v-slot:selection="{ item, index }">
                                <v-chip small label color="primary" v-if="index < 5">
                                    <span>{{ item }}</span>
                                </v-chip>
                                <span
                                    v-if="index === 5"
                                    class="grey--text text-caption"
                                >
                                    +{{ selectedWorkspaces.length - 5 }} {{ $t('label.others')}}
                                </span>
                            </template>
                        </v-select>
                    </v-col>
                    <v-col :md="3">
                        <v-menu
                            v-model="menuDateRange"
                            :close-on-content-click="false"
                            :max-width="290"
                            offset-y
                        >
                            <template v-slot:activator="{ on, attrs }">
                                <v-text-field
                                    @click:clear="dateRange = null"
                                    :value="formattedDateRange"
                                    :label="$t('label.dates')"
                                    prepend-icon="mdi-calendar"
                                    v-bind="attrs"
                                    hide-details
                                    v-on="on"
                                    readonly
                                />
                            </template>
                            <v-date-picker
                                @change="menuDateRange = false"
                                v-model="dateRange"
                                range
                            />
                        </v-menu>
                    </v-col>
                </v-row>
            </v-toolbar>
        </template>
        <template v-slot:[`item.date`]="{ item }">
            <span v-html="renderDate(item.date)" />
        </template>
    </v-data-table>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import renderMixin from "@/mixins/render"
import moment from "moment"
import http from "@/utils/http"

export default defineComponent({
    components: {},
    mixins: [renderMixin],
    data: (vm) => ({
        headersHistory: [
            { text: vm.$t("label.date"), value: "date", width: "15%"},
            { text: vm.$t("label.user"), value: "user", width: "20%" },
            { text: vm.$t("label.workspace"), value: "workspace", width: "20%" },
            { text: vm.$t("label.action"), value: "action", width: "45%" },
        ],
        options: {},
        search: "",
        sortBy: 'date',
        sortDesc: true,
        workspaces: [],
        users: [],
        items: [],
        loading: false,
        totalLine: 0,
        selectedUsers: [],
        menuDateRange: false,
        selectedWorkspaces: [],
        dateRange: [
            moment().subtract(1, "month").startOf("day").format(),
            moment().endOf("day").format()
        ]
    }),

    watch: {
        options: {
            handler () {
                this.getHistory()
            },
            deep: true
        },

        dateRange() {
            this.getHistory()
        },
        selectedWorkspaces() {
            this.getHistory()
        },
        selectedUsers() {
            this.getHistory()
        }
    },

    computed: {
        formattedDateRange() {
            const format = "DD MMMM YYYY"
            return `${moment(this.dateRange[0]).format(format)} ${this.$t('label.to')} ${moment(this.dateRange[1]).format(format)}`
        }
    },

    beforeMount() {
        this.getDependencies()
    },

    methods: {
        async getDependencies() {
            const response = await http.get("/pro/api/v1/history/search_info")
            this.workspaces = response.data.workspaces
            this.users = response.data.users
        },

        getHistory() {
            const sort_order = this.options.sortDesc[0] ? "desc" : "asc"
            const params = {
                search: this.search,
                page: this.options.page,
                per_page: this.options.itemsPerPage,
                sort: `${this.options.sortBy[0]}|${sort_order}`,
                date_from: moment.utc(this.dateRange[0]).startOf("day").format(),
                date_to: moment.utc(this.dateRange[1]).endOf("day").format(),
                users: this.selectedUsers,
                workspaces: this.selectedWorkspaces
            }

            if (!this.options.sortBy[0]) {
                delete params.sort
            }

            this.loading = true
            http.post("/pro/api/v1/history/", params)
                .then((response) => {
                    this.totalLine = response.data.total
                    this.items = response.data.data
                }).then(() => {
                    this.loading = false
                })
        }
    }
})
</script>
