<template>
    <v-hover v-slot="{ hover }">
        <v-bottom-navigation :dark="hover">
            <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                    <v-btn
                        v-on="on"
                        v-bind="attrs"
                        block
                        @click.stop="share"
                        :style="{ 'background-color': hover ? '#daab39' : '' }"
                    >
                        {{ $t('label.share') }}
                        <v-icon>mdi-share</v-icon>
                    </v-btn>
                </template>
                <span>{{ $t("help.share_workspace") }}</span>
            </v-tooltip>
        </v-bottom-navigation>
    </v-hover>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import EventBus from "@/event"

export default defineComponent({
    props: {
        workspace: {
            type: Object,
            required: true
        }
    },

    methods: {
        share() {
            EventBus.$emit('shareWorkspace', this.workspace._id)
        }
    }
})
</script>
