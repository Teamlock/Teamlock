<template>
    <v-app id="inspire">
        <app-bar />

        <v-navigation-drawer ref="drawer" app permanent :width="300">
            <router-link to="/">
                <v-img v-if="$vuetify.theme.dark"
                    class="mx-auto px-10 logoDark border-bottom-primary"
                    :src="logoWhite"
                    contain
                    width="100%"
                    height="100"
                />
                <v-img v-else
                    class="mx-auto px-10 logo border-bottom-primary"
                    :src="logo"
                    contain
                    width="100%"
                    height="100"
                />
            </router-link>

            <v-divider />

            <v-list
                class="pt-0"
                dense
            >
                <v-list-item link :to="{ name: 'Profile' }" exact>
                    <v-list-item-icon>
                    <v-icon>mdi-account-circle</v-icon>
                    </v-list-item-icon>
                    <v-list-item-title>{{ $t('label.profile') }}</v-list-item-title>
                </v-list-item>
                <v-list-item link :to="{ name: 'Sessions' }" exact>
                    <v-list-item-icon>
                    <v-icon>mdi-account-clock</v-icon>
                    </v-list-item-icon>
                    <v-list-item-title>{{ $t('label.sessions') }}</v-list-item-title>
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

export default defineComponent({
    components: { AppBar },
    mixins: [KeepAliveMixin],

    data: () => ({
        logo: require("@/assets/img/TLAppLogo_Baseline.svg"),
        logoWhite: require("@/assets/img/TLAppLogo_White.svg"),
    }),

    computed: {
        key() {
           return this.$route.path
        }
    },

    mounted() {

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