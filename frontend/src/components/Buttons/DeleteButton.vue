<template>
    <v-hover v-slot="{ hover }">
        <v-bottom-navigation :dark="hover">
            <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                    <v-btn
                        v-on="on"
                        v-bind="attrs"
                        block
                        @click.stop="deleteWorkspace"
                        :style="{ 'background-color': hover ? '#D32F2F' : ''}"
                    >
                        {{ $t('label.delete') }}
                        <v-icon>mdi-delete</v-icon>
                    </v-btn>
                </template>
                <span>{{ $t("help.delete_workspace") }}</span>
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
        deleteWorkspace() {
            EventBus.$emit("deleteWorkspace", this.workspace)
        }
    }
})
</script>
