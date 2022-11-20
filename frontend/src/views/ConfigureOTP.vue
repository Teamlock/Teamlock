<template>
    <v-app :class="renderClassBG()">
        <v-card
            tile
            class="justify-center totp-config"
            elevation="10"
        >
            <img v-if="$vuetify.theme.dark" :src="logo_light" class="mt-5"/>
            <img v-else :src="logo_dark" class="mt-5"/>

            <v-card-text class="pt-5">
                <totp-configuration />
            </v-card-text>
        </v-card>
    </v-app>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import renderMixin from "@/mixins/render"
import TotpConfigurationVue from '@/components/TotpConfiguration.vue';

export default defineComponent({
    components: {
        "totp-configuration" : TotpConfigurationVue
    },

    data : () => ({
        logo_light: require("@/assets/img/TLAppLogo_White.svg"),
        logo_dark: require("@/assets/img/TLAppLogo_Baseline.svg"),
    }), 

    mixins: [renderMixin]
})
</script>
<style scoped>
.totp-config{
    margin: 5% auto; 
    padding: 0 20px 20px 20px;
    width:500px;
}
</style>
