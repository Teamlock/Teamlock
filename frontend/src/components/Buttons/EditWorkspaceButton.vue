<template>
    <v-hover v-slot="{ hover }">
        <v-bottom-navigation :dark="hover">
            <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                    <v-btn
                        v-on="on"
                        v-bind="attrs"
                        block
                        @click="editWorkspace(workspace)"
                        :style="{ 'background-color': hover ? '#daab39' : '' }"
                    >
                        {{ $t('label.edit') }}
                        <v-icon>mdi-pencil</v-icon>
                    </v-btn>
                </template>
                <span>{{ $t("help.edit_workspace") }}</span>
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
        editWorkspace() {
            EventBus.$emit("editWorkspace", this.workspace)
        },
    }
})
</script>
