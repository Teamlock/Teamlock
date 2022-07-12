<template>
    <v-card class="mx-auto text-left" :style="cardStyle" max-width="400" flat>
        <v-app-bar flat dense>
            <v-app-bar-nav-icon v-if="args.icon">
                <v-icon>{{ args.icon }}</v-icon>
            </v-app-bar-nav-icon>
            <v-toolbar-title class="pl-0">
                {{ args.name }}
            </v-toolbar-title>
        </v-app-bar>

        <v-card-text>
            <v-row dense>
                <v-col>
                    <v-btn
                        @click="$emit('editWorkspace')"
                        color="primary"
                        elevation="2"
                        rounded
                        x-small
                        block
                    >
                        <v-icon>mdi-pencil</v-icon>
                        {{ $t('label.edit') }}
                    </v-btn>
                </v-col>
                <v-col>
                    <v-btn
                        elevation="2"
                        color="secondary"
                        rounded
                        small
                        block
                    >
                        <v-icon>mdi-share</v-icon>
                        {{ $t('label.share') }}
                    </v-btn>
                </v-col>
            </v-row>
            <v-row>
                <p><v-icon>mdi-folder</v-icon>: {{ args.nb_folders}}</p>
                <p><v-icon>mdi-key</v-icon>: {{ args.nb_keys}}</p>
            </v-row>
        </v-card-text>
    </v-card>
</template>

<script>
import renderMixin from "@/mixins/render"
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
    mixins: [renderMixin],

    props: {
        args: {
            type: Object,
            required: true
        }
    }
})
</script>
