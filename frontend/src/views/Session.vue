<template>
    <v-data-table
        dense
        :headers="headersSessions"
        :items="sessions"
        elevation="5"
        :options.sync="options"
        :server-items-length="totalSessions"
        :sort-by="sortBy"
        :sort-desc="sortDesc"
        :loading="is_loading"
    >
        <template v-slot:[`item.date`]="{ item }">
            <span v-html="renderDate(item.date)" />
        </template>
        <template v-slot:[`item.os`]="{ item }">
            <v-icon v-html="renderOS(item.os)" />
            {{ item.os }}
        </template>
        <template v-slot:[`item.country`]="{ item }">
            <v-img v-if="item.country" :src="renderCountry(item.country)" width="20"/>
        </template>
    </v-data-table>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import { mapGetters } from 'vuex'
import renderMixin from "@/mixins/render"
import http from "@/utils/http"

export default defineComponent({
    mixins: [renderMixin],

    data: (vm) => ({
        headersSessions: [
            { text: vm.$t('label.date'), value: 'date', width: 200 },
            { text: vm.$t('label.ip'), value: 'ip_address', width: 150 },
            { text: vm.$t('label.os'), value: 'os', width: 100 },
            { text: vm.$t('label.user_agent'), value: 'user_agent' },
            { text: vm.$t('label.country'), value: 'country' },
            { text: vm.$t('label.city'), value: 'city' },
        ],
        options: {
            itemsPerPage: 20
        },
        sessions: [],
        sortBy: "date",
        sortDesc: true,
        is_loading: false,
        totalSessions: 0
    }),
    computed: {
        ...mapGetters({
            user: 'getUser'
        })
    },

    watch: {
        options: {
            handler () {
                this.getUserSession()
            },
            deep: true
        }
    },

    mounted() {},

    methods: {
        getUserSession() {
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
            http.get("/api/v1/user/sessions", { params: params }).then((response) => {
                this.totalSessions = response.data.total
                this.sessions = response.data.data
            }).then(() => {
                this.loading = false
            })
        }
    }
})
</script>
