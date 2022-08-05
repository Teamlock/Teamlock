<template>
  <draggable
    :list="secrets"
    tag="tr"
    @start="startDrag"
    @end="endDrag"
    class="text-left"
    :key="item._id"
    :id="item._id"
  >
    <td>{{ item.name.value }}</td>
    <td>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <span 
            class="cursor"
            v-on:click.stop
            v-on:dblclick.stop="copyData('login', item)"
            v-bind="attrs"
            v-on="on"
          >
            {{ item.login.value }}
          </span> 
        </template>
        <span>{{ $t('tooltip.dblclick_copy') }}</span>
      </v-tooltip>
    </td>
    <td>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <span 
            class="cursor"
            v-on:click.stop
            v-on:dblclick.stop="copySecret(item._id)"
            v-bind="attrs"
            v-on="on"
            @contextmenu.prevent="can_share_external && is_pro? $refs.menuKey.open($event, item) : ''"
          >
            <span v-if="!loader_secrets[item._id]">
              *********
            </span>
            <v-progress-circular v-else :width="2" :size="20" indeterminate color="primary"/>
            <v-btn 
              v-if="can_share_external && is_pro"
              @click="$refs.menuKey.open($event, item)"
              style="float: right"
              x-small
              color="primary"
              icon
              >
                <v-icon>mdi-share-all</v-icon>
              </v-btn>
          </span>
        </template>
        <span>{{ $t('tooltip.dblclick_copy') }}</span>
      </v-tooltip>
    </td>
    <td>
      <span v-if="item.url.value !== ''">
        <v-btn
          :href="item.url.value" 
          color="primary"
          target="_blank"
          x-small
          right
          icon
          link 
        >
          <v-icon>mdi-open-in-new</v-icon>
        </v-btn>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <span 
              class="cursor"
              v-on:click.stop
              v-on:dblclick.stop="copyData('url', item)"
              v-bind="attrs"
              v-on="on"
            >
              {{ item.url.value | str_limit(40) }}
            </span>
          </template>
          <span>{{ $t('tooltip.dblclick_copy') }}</span>
        </v-tooltip>
      </span>
    </td>
    <td>{{ item.ip.value }}</td>

    <td class="text-right">
      <v-menu :close-on-content-click="false"  left offset-y>
        <template v-slot:activator="{ on, attrs }">
          <v-icon small v-on="on" class="mr-2" v-bind="attrs">
            mdi-information
          </v-icon>
        </template>
        <v-card width="500" max-height="500" class="text-left scroll"  flat>
          <v-app-bar flat dense class="edit_workspace_bar">
            <v-toolbar-title>{{ $t('label.last_update')}}: <strong>{{ renderDate(item.updated_at) }}</strong></v-toolbar-title>
          </v-app-bar>
          <v-card-text>
            <pre>{{ item.informations.value }}</pre>
          </v-card-text>
        </v-card>
      </v-menu>
      <v-tooltip
          v-model="tooltip_copy_password[item._id]"
          bottom
      >
          <template v-slot:activator="{ on, attrs }">
            <v-icon
                @click.stop="copySecret(item._id, 'password')"
                v-bind="attrs"
                v-on="on"
                class="mr-2"
                small
            >
                mdi-content-copy
            </v-icon>
          </template>
          <span v-html="tooltipSecretId" />
      </v-tooltip>
      <span v-if="(selected_workspace.owner === user._id || selected_workspace.can_write)">
        <v-tooltip bottom v-if="!in_trash">
          <template v-slot:activator="{ on, attrs }">
            <v-icon
              small
              v-on="on"
              class="mr-2"
              v-bind="attrs"
              @click.stop="editSecret(category, item)"
            >
              mdi-pencil
            </v-icon>
          </template>
          <span>{{ $t('help.edit_key') }}</span>
        </v-tooltip>
        <v-menu offset-y left>
          <template v-slot:activator="{ on: menu, attrs }">
            <v-tooltip bottom>
              <template v-slot:activator="{ on: tooltip }">
                <v-icon
                  small
                  v-bind="attrs"
                  v-on="{ ...tooltip, ...menu }"
                  @click.stop
                >
                  mdi-delete
                </v-icon>
              </template>
              <span>{{ $t('help.delete_key')}}</span>
            </v-tooltip>
          </template>
          <v-card>
            <v-card-title style="font-size: 16px">
              <small>
                <v-icon>mdi-alert</v-icon> 
                {{$t('warning.confirm_delete')}}
              </small>
            </v-card-title>
            <v-card-actions>
              <v-spacer></v-spacer>
                <v-btn small text>{{ $t('button.cancel') }}</v-btn>
                <v-btn small color="primary" text @click="deleteItem(item)">{{ $t('button.confirm') }}</v-btn>
            </v-card-actions>
          </v-card>
        </v-menu>
      </span>
    </td>
  </draggable>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import secretMixin from "@/mixins/secrets"
import renderMixin from "@/mixins/render"
import { mapGetters } from 'vuex'

export default defineComponent({
  mixins: [secretMixin, renderMixin],

  props: {
    can_share_external: {
      type: Boolean,
      required: true
    },

    secrets: {
      type: Array,
      required: true
    },

    item: {
      type: Object,
      required: true
    }
  },

  computed: {
      ...mapGetters({
        user: 'getUser',
        selected_workspace: "getWorkspace"
      }),
  }
})
</script>
