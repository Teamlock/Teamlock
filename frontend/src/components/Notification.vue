<template>
    <v-menu
        v-model="menu"
        :close-on-content-click="false"
        :nudge-width="450"
        offset-y
        :rounded="false"
        left
    >
        <template v-slot:activator="{ on, attrs }">
            <v-badge
                :value="notifications.length > 0"
                bordered
                color="primary"
                :content="notifications.length"
                class="mr-5"
                overlap
            >
                <v-btn
                    color="primary"
                    v-bind="attrs"
                    v-on="on"
                    class="mr-0 ml-2"
                    small
                    icon
                >
                    <v-icon color="dark">
                        {{ !notifications.length ? 'mdi-bell' : 'mdi-bell-ring' }}
                    </v-icon>
                </v-btn>
            </v-badge>
        </template>

        <v-card
            class="mx-auto"
            max-width="500"
        >
            <v-toolbar
                color="primary"
                dark
                dense
            >
                <v-icon class="mr-4">mdi-bell-ring</v-icon>
                <v-toolbar-title>{{ $t('title.notifications') }}</v-toolbar-title>
                <v-spacer />
                <v-tooltip bottom>
                    <template v-slot:activator="{ on, attrs }">
                        <v-icon
                            @click="emptyNotifications()"
                            :loading="clean_loading"
                            v-bind="attrs"
                            v-on="on"
                            dark
                        >
                            mdi-cancel
                        </v-icon>
                    </template>
                    <span>{{ $t('help.clear_notification') }}</span>
                </v-tooltip>
            </v-toolbar>

            <v-list v-if="notifications.length === 0">
                <v-list-item>
                    <v-list-item-content>
                        <v-list-item-title v-text="$t('label.no_notifications')" />
                    </v-list-item-content>
                </v-list-item>
            </v-list>

            <v-expansion-panels tile>
                <v-expansion-panel
                    v-for="(item, i) in notifications"
                    :key="i"
                >
                    <v-expansion-panel-header style="padding: 0 10px">
                        <v-row no-gutters>
                            <v-col :md="6">
                                {{ $t(`notifications.${item.message}`) }}
                            </v-col>
                            <v-col :md="6" class="text-right">
                                <span class="caption">
                                    {{ renderDate(item.date) }}
                                </span>
                            </v-col>
                        </v-row>
                    </v-expansion-panel-header>
                    <v-expansion-panel-content>
                        <v-card tile class="text-left">
                            <v-card-subtitle>
                                {{ $t(`notifications.details.${item.message}`) }}
                            </v-card-subtitle>
                            <v-card-text>
                                <table style="width: 100%" class="mb-4">
                                    <thead>
                                        <tr>
                                            <th>{{ $t('label.user') }}</th>
                                            <th>{{ $t('label.country') }}</th>
                                            <th>{{ $t('label.city') }}</th>
                                            <th>{{ $t('label.os') }}</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>{{ item.user.email }}</td>
                                            <td>
                                                <v-img
                                                    v-if="item.client_info.country"
                                                    :src="renderCountry(item.client_info.country)"
                                                    style="float: left"
                                                    class="mr-2"
                                                    width="20"
                                                />
                                                {{ item.client_info.country.toUpperCase() }}
                                            </td>
                                            <td>{{ item.client_info.city }}</td>
                                            <td>{{ item.client_info.os }}</td>
                                        </tr>
                                    </tbody>
                                </table>
                                <table style="width: 100%" v-if="item.secret">
                                    <thead>
                                        <tr>
                                            <th>{{ $t('label.secret_name') }}</th>
                                            <th>{{ $t('label.folder') }}</th>
                                            <th>{{ $t('label.workspace') }}</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>{{ item.secret.name }}</td>
                                            <td>{{ item.secret.folder }}</td>
                                            <td>{{ item.secret.workspace }}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </v-card-text>
                            <v-card-actions>
                                <v-btn
                                    @click="ackNotification(item, i)"
                                    text
                                    color="primary"
                                    :loading="loading[i]"
                                    small
                                    v-html="$t('button.notification_read')"
                                />
                            </v-card-actions>
                        </v-card>
                    </v-expansion-panel-content>
                </v-expansion-panel>
            </v-expansion-panels>
        </v-card>
    </v-menu>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import renderMixin from "@/mixins/render"
import http from "@/utils/http"

export default defineComponent({
    mixins: [renderMixin],

    data: () => ({
        notifications: [],
        loading: [],
        clean_loading: false,
        interval: null,
        menu: false
    }),

    mounted() {
        this.getNofications()
        this.interval = setInterval(() => {
            this.getNofications()
        }, 10000)
    },

    destroyed() {
        if (this.interval) {
            clearInterval(this.interval)
        }
    },

    methods: {
        async getNofications() {
            const { data } = await http.get("/pro/api/v1/notif/")
            this.notifications = data
        },

        ackNotification(notif, i) {
            const url = `/pro/api/v1/notif/${notif._id}`
            this.loading[i] = true
            this.$forceUpdate()
            setTimeout(() => {
                http.delete(url).then(() => {
                    this.loading[i] = false
                    this.notifications.splice(i, 1)
                    this.$toast.success(this.$t('success.notif_ack'), {
                        closeOnClick: true,
                        timeout: 3000,
                        icon: true
                    })
                })
            }, 1000);
        },

        emptyNotifications() {
            this.clean_loading = true
            http.delete("/pro/api/v1/notif/all")
            .then(() => {
                this.notifications = []
                this.$toast.success(this.$t('success.notif_cleaned'), {
                    closeOnClick: true,
                    timeout: 3000,
                    icon: true
                })
            })
            .then(() => {
                this.clean_loading = false
            })
        }
    }
})
</script>

<style>
.v-expansion-panel-content__wrap{
    padding: 0px !important;
}
</style>