<template>
  <span>
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
    <v-menu
      v-if="can_share_external && is_pro"
      offset-y
      left
    >
      <template v-slot:activator="{ on: menu, attrs }">
        <v-tooltip bottom>
          <template v-slot:activator="{ on: tooltip }">
            <v-icon
              small
              v-bind="attrs"
              class="mr-2"
              v-on="{ ...tooltip, ...menu }"
              @click.stop
            >
              mdi-share-all
            </v-icon>
          </template>
          <span>{{ $t('help.external_share')}}</span>
        </v-tooltip>
      </template>
      <v-card>
        <context-key :data="item" :sms="twilioEnabled" />
      </v-card>
    </v-menu>
    <v-tooltip
        v-model="tooltip_copy"
        bottom
    >
        <template v-slot:activator="{ on, attrs }">
          <v-icon
              @click.stop="copyData(item._id)"
              v-bind="attrs"
              v-on="on"
              class="mr-2"
              small
          >
              mdi-content-copy
          </v-icon>
        </template>
        <span v-html="tooltipHTML" />
    </v-tooltip>
    <span v-if="(selected_workspace.owner === user._id || selected_workspace.can_write)">
      <v-tooltip bottom>
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
              <v-btn small color="primary" text @click="$emit('delete', item)">
                {{ $t('button.confirm') }}
              </v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>
      <v-menu offset-y left v-if="showTrash">
        <template v-slot:activator="{ on: menu, attrs }">
          <v-tooltip bottom>
            <template v-slot:activator="{ on: tooltip }">
              <v-icon
                small
                v-bind="attrs"
                v-on="{ ...tooltip, ...menu }"
                @click.stop
              >
                mdi-delete-empty
              </v-icon>
            </template>
            <span>{{ $t('help.restore_key')}}</span>
          </v-tooltip>
        </template>
        <v-card>
          <v-card-title style="font-size: 16px">
            <small>
              <v-icon>mdi-alert</v-icon> 
              {{$t('warning.confirm_restore_key')}}
            </small>
          </v-card-title>
          <v-card-actions>
            <v-spacer></v-spacer>
              <v-btn small text>{{ $t('button.cancel') }}</v-btn>
              <v-btn small color="primary" text @click="$emit('restore', item)">
                {{ $t('button.confirm') }}
              </v-btn>
          </v-card-actions>
        </v-card>
      </v-menu>
    </span>
    <portal to="contextMenuKey">
      <vue-context ref="menuKey" v-slot="{ data }" class="p-0">
        <context-key :data="data" :sms="twilioEnabled"/>
      </vue-context>
    </portal>
  </span>
</template>

<script>
import ContextKey from '@/components/Context/ContextKey.vue'
import { defineComponent } from '@vue/composition-api'
import secretMixin from "@/mixins/secrets"
import renderMixin from "@/mixins/render"
import VueContext from 'vue-context';
import { mapGetters } from 'vuex'
import EventBus from "@/event"

export default defineComponent({
  mixins: [secretMixin, renderMixin],

  components: {
    VueContext,
    ContextKey
  },

  props: {
    item: {
      type: Object,
      required: true
    },

    category: {
      type: String,
      required: true
    },

    can_share_external: {
      type: Boolean,
      required: true
    }
  },

  data: (vm) => ({
    tooltip_copy: false,
    tooltipHTML: vm.$t('tooltip.copy_id'),
    twilioEnabled: false,
    is_pro: false,
    showTrash: false
  }),

  beforeMount() {
    this.is_pro = this.$store.state.pro
    this.twilioEnabled = this.$store.state.twilio
  },

  mounted() {
    EventBus.$on("showTrash", val => {
      this.showTrash = val
    })
    this.showTrash = localStorage.getItem("showTrash") === "true";
  },

  computed: {
    ...mapGetters({
      user: 'getUser',
      selected_workspace: "getWorkspace"
    }),
  },

  methods: {
    openContextMenu($event, item) {
      if (this.can_share_external && this.is_pro) {
        this.$refs.menuKey.open($event, item)
      }
    },

    editSecret(secret_type, secret) {
      EventBus.$emit(`edit_${secret_type}`, secret._id)
    },

    copySuccess() {
      setTimeout(() => {
        this.tooltipHTML = this.$t("help.copied")
        this.tooltip_copy = true

        setTimeout(() => {
          this.tooltip_copy = false

          setTimeout(() => {
            this.tooltipHTML = this.$t("tooltip.copy_id")
          }, 500);
        }, 1000);
      }, 50);
    },

    copyData(value_to_copy) {
      if (!this.electron) {
        this.$copyText(value_to_copy)
        this.copySuccess()
        
      } else {
        window.ipc.send("COPY", value_to_copy)
        window.ipc.on("COPY", () => {
          this.tooltipHTML = this.$t("help.copied")
          this.copySuccess()
        })
      }
    },
  }
})
</script>
