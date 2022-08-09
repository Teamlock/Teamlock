<template>
    <v-app id="inspire">
        <app-bar />

        <v-navigation-drawer ref="drawer" app permanent :width="300">
            <router-link to="/">
                <v-img 
                    :class="logoClass"
                    :src="logo"
                    width="100%"
                    height="100"
                    contain
                />
            </router-link>
            <v-divider />
            <v-list dense class="pt-0">
                <v-list-item :to="{ name: 'Admin' }" exact>
                    <v-list-item-icon><v-icon>mdi-cogs</v-icon></v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('label.admin') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
                <v-list-item :to="{ name: 'Users' }" exact>
                    <v-list-item-icon><v-icon>mdi-account-group</v-icon></v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('label.users') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
                <v-list-item :to="{ name: 'History' }" exact v-if="is_pro">
                    <v-list-item-icon><v-icon>mdi-clock</v-icon></v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('label.history') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list>
        </v-navigation-drawer>

        <v-main>
            <router-view />
        </v-main>
    </v-app>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import KeepAliveMixin from "@/mixins/keepalive"
import AppBar from '../components/AppBar.vue'
import designMixin from "@/mixins/design"

export default defineComponent({
    components: { AppBar },
    mixins: [KeepAliveMixin, designMixin],

    data: () => ({
        is_pro: false,
    }),

    computed: {
        key() {
           return this.$route.path
        }
    },

    beforeMount() {
        this.is_pro = this.$store.state.pro
    },

    methods: {
  },
})
</script>

<style>
#logo {
    margin: 0 auto;
}
</style>