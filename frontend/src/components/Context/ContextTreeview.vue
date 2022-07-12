<template>
    <div>
        <v-list dense style="text-align: left" color="primary" v-if="selected_workspace">
            <v-subheader>
                <v-icon style="margin-right: 5px">mdi-file-tree</v-icon>
                <b style="font-size: 15px">{{ selected_workspace.name }}</b>
            </v-subheader>
            <v-divider />
            <v-list-item-group color="primary" v-model="selectedMenu">
                <v-list-item>
                    <v-list-item-icon class="mr-2">
                        <v-icon :size="17">mdi-plus</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                        <v-list-item-title>{{ $t('folder.add') }}</v-list-item-title>
                    </v-list-item-content>
                </v-list-item>
            </v-list-item-group>
        </v-list>
    </div>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import { mapGetters } from 'vuex'
import EventBus from "@/event"

export default defineComponent({
    data: () => ({
        selectedMenu: null
    }),

    computed: {
        ...mapGetters({
            selected_workspace: 'getWorkspace'
        })
    },

    watch: {
        selectedMenu(val) {
            if (val === null) return
            switch(val) {
                case 0:
                    this.addFolder();
                    break
            }

            this.selectedMenu = null
        }
    },

    mounted() {},

    methods: {
        addFolder() {
            EventBus.$emit("editFolder")
        }
    }
})
</script>
<style scoped>
.v-list{
    padding: 0;
}

.v-list-item__content {
    margin-left: 10px;
}

.v-list-item--link:hover {
    background-color: #fccb58;
    color: #fff !important;
}
</style>