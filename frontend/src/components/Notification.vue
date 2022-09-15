<template>
    <v-menu
        v-model="menu"
        :close-on-content-click="false"
        :nudge-width="400"
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
            </v-toolbar>

            <v-list v-if="items.length === 0">
                <v-list-item>
                    <v-list-item-content>
                        <v-list-item-title v-text="$t('label.no_notifications')" />
                    </v-list-item-content>
                </v-list-item>
            </v-list>

            <v-expansion-panels tile>
                <v-expansion-panel
                    v-for="(item, i) in items"
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
                                <table style="width: 100%">
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
                            </v-card-text>
                            <v-card-actions>
                                <v-btn
                                    @click="setNotificationRead(item, i)"
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
        readNotifications: [],
        notifications: [],
        selectedNotRead: [],
        showReadNotif: false,
        loading: [],
        menu: false
    }),

    computed: {
        items() {
            return this.showReadNotif ? this.readNotifications : this.notifications
        }
    },

    mounted() {
        this.getNofications()
        this.getReadNotification()
    },

    methods: {
        async getNofications() {
            const response = await http.get("/pro/api/v1/notif")
            this.notifications = response.data
        },

        async getReadNotification() {
            const response = await http.get("/pro/api/v1/notif", {params: {read: true}})
            this.readNotifications = response.data
        },

        setNotificationRead(notif, index) {
            this.loading[index] = true
            const url = `/pro/api/v1/notif/${notif._id}`
            http.delete(url).then(() => {
                this.notifications.splice(index, 1)
            }).then(() => {
                this.loading[index] = false
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