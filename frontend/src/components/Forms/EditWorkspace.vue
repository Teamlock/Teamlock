<template>
    <v-bottom-navigation :height="50">
        <v-menu
            :close-on-content-click="false"
            :close-on-click="false"
            :nudge-width="400"
            v-model="open"
            offset-x
            right
        >
            <template v-slot:activator="{ on: menu, attrs }">
                <v-tooltip bottom>
                    <template v-slot:activator="{ on: tooltip }">
                        <v-btn
                            block
                            tile
                            small
                            :height="50"
                            v-bind="attrs"
                            v-on="{ ...tooltip, ...menu }"
                        >
                            <small><i>{{ $t('label.create') }}</i></small>
                            <v-icon color="#daab39">mdi-plus-box</v-icon>
                        </v-btn>
                    </template>
                    <span>{{ $t('help.create_workspace') }}</span>
                </v-tooltip>
            </template>
            <v-form
                ref="form"
                v-model="valid"
                lazy-validation
                @submit.prevent="saveWorkspace"
            >
                <v-card :loading="loading" class="mx-auto" :min-width="400" :max-height="800">
                    <v-app-bar flat dense class="edit_workspace_bar">
                        <v-app-bar-nav-icon>
                            <span v-if="!workspace">
                                <v-icon class="mr-2">mdi-plus-circle</v-icon>
                            </span>
                            <span v-else-if="workspace.icon">
                                <v-icon class="mr-2">{{ workspace.icon }}</v-icon>
                            </span>
                            <span v-else>
                                <v-icon>mdi-view-dashboard</v-icon>
                            </span>
                        </v-app-bar-nav-icon>
                        <v-toolbar-title class="pl-0">
                            <span v-if="!workspace">
                                {{ $t('label.create_workspace') }}
                            </span>
                            <span v-else>{{ workspace.name }}</span>
                        </v-toolbar-title>
                    </v-app-bar>
                
                    <v-card-text class="pb-0">
                        <v-row dense>
                            <v-col>
                                <v-text-field
                                    ref="workspaceName"
                                    v-model="form.name"
                                    :label="$t('label.workspace_name')"
                                    :counter="8"
                                    maxlength="8"
                                />
                            </v-col>
                        </v-row>

                        <v-row dense>
                            <v-select 
                                :items="iconsList"
                                v-model="form.icon"
                                :label="$t('label.select_icon')"
                                item-text="text"
                                item-value="icon"
                            >
                                <template slot="selection" slot-scope="data">
                                    <v-icon class="mr-1">{{data.item.icon}}</v-icon> {{ data.item.text }}
                                </template>
                                <template slot="item" slot-scope="data">
                                    <v-icon class="mr-1">{{data.item.icon}}</v-icon> {{ data.item.text }}
                                </template>
                            </v-select>
                        </v-row>

                        <v-row dense>
                            <v-col>
                                <v-switch 
                                    v-model="form.custom_policy"
                                    class="m-0"
                                    :label="$t('label.password_policy')"
                                    hide-details
                                />
                            </v-col>
                        </v-row>
                        <span>
                            <v-row>
                                <p class="mt-5 ml-3">
                                    <small>
                                        <v-icon>mdi-information-outline</v-icon> {{ $t('help.policy_password_workspace') }}
                                    </small>
                                </p>
                            </v-row>
                            <v-row dense>
                                <v-col class="text-left">
                                    <label>{{ $t('label.password_length') }}</label>
                                    <v-slider
                                        :disabled="!form.custom_policy"
                                        v-model="form.password_policy.length"
                                        max="100"
                                        min="0"
                                        track-color="#E2E2E2"
                                    >
                                        <template v-slot:append>
                                            <v-text-field
                                                v-model="form.password_policy.length"
                                                class="mt-0 pt-0"
                                                :disabled="!form.custom_policy"
                                                hide-details
                                                single-line
                                                type="number"
                                                style="width: 60px"
                                            />
                                        </template>
                                    </v-slider>
                                </v-col>
                            </v-row>
                            <v-row dense>
                                <v-col class="text-left">
                                    <label>{{ $t('label.password_upper') }}</label>
                                    <v-slider
                                        :disabled="!form.custom_policy"
                                        v-model="form.password_policy.uppercase"
                                        :max="form.password_policy.length"
                                        min="0"
                                        track-color="#E2E2E2"
                                    >
                                        <template v-slot:append>
                                            <v-text-field
                                                v-model="form.password_policy.uppercase"
                                                class="mt-0 pt-0"
                                                :disabled="!form.custom_policy"
                                                hide-details
                                                single-line
                                                type="number"
                                                style="width: 60px"
                                            />
                                        </template>
                                    </v-slider>
                                </v-col>
                            </v-row>
                            <v-row dense>
                                <v-col class="text-left">
                                    <label>{{ $t('label.password_number') }}</label>
                                    <v-slider
                                        :disabled="!form.custom_policy"
                                        v-model="form.password_policy.numbers"
                                        :max="form.password_policy.length - form.password_policy.uppercase"
                                        min="0"
                                        track-color="#E2E2E2"
                                    >
                                        <template v-slot:append>
                                            <v-text-field
                                                v-model="form.password_policy.numbers"
                                                class="mt-0 pt-0"
                                                :disabled="!form.custom_policy"
                                                hide-details
                                                single-line
                                                type="number"
                                                style="width: 60px"
                                            />
                                        </template>
                                    </v-slider>
                                </v-col>
                            </v-row>
                            <v-row dense>
                                <v-col class="text-left">
                                    <label>{{ $t('label.password_special') }}</label>
                                    <v-slider
                                        :disabled="!form.custom_policy"
                                        v-model="form.password_policy.special"
                                        :max="form.password_policy.length - (form.password_policy.uppercase + form.password_policy.numbers)"
                                        min="0"
                                        track-color="#E2E2E2"
                                    >
                                        <template v-slot:append>
                                            <v-text-field
                                                v-model="form.password_policy.special"
                                                class="mt-0 pt-0"
                                                :disabled="!form.custom_policy"
                                                hide-details
                                                single-line
                                                type="number"
                                                style="width: 60px"
                                            />
                                        </template>
                                    </v-slider>
                                </v-col>
                            </v-row>
                        </span>
                    </v-card-text>

                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn text small @click="closeMenu">{{ $t('button.cancel') }}</v-btn>
                        <v-btn small color="primary" text type="submit">{{ $t('button.submit') }}</v-btn>
                    </v-card-actions>
                </v-card>
            </v-form>
        </v-menu>
    </v-bottom-navigation>
</template>

<script>
import http from "@/utils/http";
import EventBus from "@/event"
import varMixin from "@/mixins/var"
import { defineComponent } from '@vue/composition-api'

export default defineComponent({
    mixins: [varMixin],

    components: {},

    props: {
        workspace: {
            type: Object,
            required: false
        }
    },

    beforeDestroy() {
        this.form = {
            name: "",
            icon: "mdi-web",
            custom_policy: false,
            password_policy: {
                length: 12,
                uppercase: 1,
                numbers: 1,
                special: 1
            }
        }
    },

    data: () => ({
        loading: false,
        open: false,
        valid: true,
        workspace_id: false,
        form: {
            name: "",
            icon: "mdi-web",
            custom_policy: false,
            password_policy: {
                length: 12,
                uppercase: 1,
                numbers: 1,
                special: 1  
            }
        }
    }),
    
    mounted() {
        EventBus.$on("editWorkspace", (workspace) => {
            this.open = true
            this.workspace_id = workspace._id
            this.form = {
                name: workspace.name,
                icon: workspace.icon,
            }

            if (workspace.password_policy) {
                this.form.custom_policy = true
                this.form.password_policy = workspace.password_policy
            } else {
                this.form.password_policy = {
                    length: 12,
                    uppercase: 1,
                    numbers: 1,
                    special: 1
                }
            }

            setTimeout(() => {
                this.$refs.workspaceName.focus()
            }, 500);
        })
    },

    methods: {
        closeMenu() {            
            this.form = {
                name: "",
                icon: "mdi-web",
                custom_policy: false,
                password_policy: {
                    length: 12,
                    uppercase: 1,
                    numbers: 1,
                    special: 1
                }
            }

            this.open = false
        },

        async saveWorkspace() {
            this.loading = true;
            const form = Object.assign({}, this.form);
            let uri = "/api/v1/workspace/"

            if (!form.custom_policy) {
                form.password_policy = null
            }

            if (this.workspace_id) {
                uri += this.workspace_id
                await http.put(uri, form)  
            } else {
                await http.post(uri, form)  
            }

            this.loading = false
            this.$emit("refresh")
            this.closeMenu()
        }
    }
})
</script>
