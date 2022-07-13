<template>
  <span v-if="selected_workspace" @click.stop>
    <v-data-table
        hide-default-footer
        :headers="headers"
        :loading="loading"
        class="elevation-1"
        fill-height
        :items="keys"
        item-key="_id"
        sort-by="name.value"
        :sort-desc="false"
        disable-pagination
        dense
    >
      <template v-slot:no-data="">
        <div class="restore_folder" style="margin-bottom:10px" v-if="in_trash">
          <v-icon small>mdi-alert</v-icon>
          {{$t("warning.restore")}}
        </div>
        {{ $t('label.no_data_available') }}
      </template>
      <template v-slot:[`header.actions`]="{}">
        <v-menu offset-y left  v-if="(is_trash || in_trash) && (selected_workspace.owner === user._id || selected_workspace.can_write)">
          <template v-slot:activator="{ on: menu, attrs }">
            <v-tooltip bottom>
              <template v-slot:activator="{ on: tooltip }">
                <v-icon
                  v-bind="attrs"
                  v-on="{ ...tooltip, ...menu }"
                  class="mr-2"
                  @click.stop
                >
                  mdi-delete-empty
                </v-icon>
              </template>
              <span>{{ $t('help.empty_trash') }}</span>
            </v-tooltip>
          </template>
        <v-card>
          <v-card-title style="font-size: 16px">
            <small>
              <v-icon>mdi-alert</v-icon> 
              {{$t("warning.confirm_empty_trash")}}
            </small>
          </v-card-title>
          <v-card-actions>
            <v-spacer></v-spacer>
              <v-btn small text>{{ $t('button.cancel') }}</v-btn>
              <v-btn small color="primary" text @click="emptyTrash">{{ $t('button.confirm') }}</v-btn>
          </v-card-actions>
        </v-card>
        </v-menu>
        <v-btn
          tile
          x-small
          color="primary"
          @click="addKey"
          v-if="!in_trash && (selected_workspace.owner === user._id || selected_workspace.can_write)"
        >
          <v-icon small>mdi-plus</v-icon>
          {{ $t("button.add_key") }}
        </v-btn>     
      </template>
      <template v-slot:item="{ item,index }">
        <td class="restore_folder" colspan="6" v-if="index == 0 && in_trash">
          <v-icon small>mdi-alert</v-icon>
          {{$t("warning.restore")}}
        </td>
        <draggable
          :list="keys"
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
                  v-on:dblclick.stop="copyPassword(item._id)"
                  v-bind="attrs"
                  v-on="on"
                  @contextmenu.prevent="can_share_external && is_pro? $refs.menuKey.open($event, item) : ''"
                >
                  <span v-if="!loader_keys[item._id]">
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
          <td>
            <v-menu :close-on-content-click="false"  left offset-y v-if="item.informations.value">
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
            <span v-if="(selected_workspace.owner === user._id || selected_workspace.can_write)">
              <v-tooltip bottom v-if="!in_trash">
                <template v-slot:activator="{ on, attrs }">
                  <v-icon
                    small
                    v-on="on"
                    class="mr-2"
                    v-bind="attrs"
                    @click.stop="editKey(item)"
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
    </v-data-table>
    <portal to="contextMenuKey">
      <vue-context ref="menuKey" v-slot="{ data }" class="p-0">
        <context-key :data="data" :sms="twilioEnabled"/>
      </vue-context>
    </portal>
  </span>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import ContextKey from '../components/Context/ContextKey.vue'
import renderMixin from "@/mixins/render"
import VueContext from 'vue-context';
import draggable from 'vuedraggable'
import { mapGetters } from 'vuex'
import EventBus from "@/event"
import http from "@/utils/http"

export default defineComponent({
    components: {
      VueContext,
      ContextKey,
      draggable
    },

    mixins: [renderMixin],

    data: (vm) => ({
      twilioEnabled: false,
      electron: false,
      trash:{},
      in_trash:false,
      is_trash:false,
      loading: false,
      loader_keys: {},
      is_pro: false,
      headers: [
        {
          text: vm.$t('label.name'),
          align: 'start',
          value: 'name.value',
        },
        {
          text: vm.$t('label.login'),
          align: 'start',
          value: 'login.value',
        },
        {
          text: vm.$t('label.secret'),
          align: 'start',
          value: 'password',
          sortable: false
        },
        {
          text: vm.$t('label.url'),
          align: 'start',
          value: 'url.value'
        },
        {
          text: vm.$t('label.ip'),
          align: 'start',
          value: 'ip.value',
        },
        {
          text: vm.$t('label.actions'),
          align: 'start',
          value: 'actions',
          sortable: false,
          width: "10px"
        },
      ],
      keys: [],
      can_share_external: false
    }),

    computed: {
      ...mapGetters({
        user: 'getUser',
        current_folder: 'getFolder',
        selected_workspace: "getWorkspace"
      }),

      height() {
        const height = document.getElementsByClassName("v-main__wrap")[0].offsetHeight;
        return height - 45
      }
    },

    watch: {
      current_folder() {
        this.getKeys()
      }
    },

    beforeMount() {
      const userAgent = navigator.userAgent.toLowerCase();
      this.electron = userAgent.indexOf(' electron/') > -1

      this.is_pro = this.$store.state.pro
    },

    mounted() {
      EventBus.$on("refreshKeys", () => {
        this.getKeys()
      })

      EventBus.$on("searchKeys", (search) => {
        this.searchKeys(search)
      })

      EventBus.$on("folder_trash", res =>{
        this.in_trash = res.in_trash;
        this.is_trash = res.is_trash;
        if(res.is_trash) this.in_trash = true;
      })

      EventBus.$on("empty_trash",() => this.emptyTrash());

      http.get("/api/v1/config/twilio").then((response) => {
        this.twilioEnabled = response.data
      })
    },

    methods: {
      emptyTrash(){
        this.loading = true;
        const uri = `/api/v1/workspace/${sessionStorage.getItem("current_workspace")}/trash`;
        http.delete(uri).then(() =>{
          this.keys = [];
          this.$toast.success(this.$t("success.trash_emptied"), {
            closeOnClick: true,
            timeout: 3000,
            icon: true
          })
          this.loading = false;
          EventBus.$emit("refreshTreeview");
          }).catch((error) => {
          if (error.response.status === 500) {
            this.$toast.error(this.$t("error.occurred"), {
              closeOnClick: true,
              timeout: 5000,
              icon: true
            })
          }
        })
      },
      searchKeys(search) {
        this.loading = true;
        this.keys = []

        const uri = "/api/v1/key/search"
        const params = {
          search: search,
          workspace: this.selected_workspace._id
        }

        http.get(uri, {params: params}).then((response) => {
          this.keys = response.data;
          this.loading = false
        })
      },

      getKeys() {
        if (!this.current_folder) return

        http.get(`/api/v1/workspace/${sessionStorage.getItem("current_workspace")}/trash`)
          .then(response => this.trash = response.data)

        if (this.selected_workspace.owner  === this.$store.state.user._id) {
          this.can_share_external = true
        } else {
          this.can_share_external = this.selected_workspace.can_share_external
        }

        this.loading = true;
        this.keys = [];
        const uri = `/api/v1/folder/${this.current_folder}/keys`
        http.get(uri).then((response) => {
          this.keys = response.data
          this.loading = false
        }).catch((error) => {
          if (error.response.status === 500) {
            this.$toast.error(this.$t("error.occurred"), {
              closeOnClick: true,
              timeout: 5000,
              icon: true
            })
          }
        }).then(() => {
          this.loading = false
        })
    },

    copyData(attr, key) {
      const value_to_copy = key[attr].value
      if (!this.electron) {
        this.$copyText(value_to_copy)
        this.copySuccess(this.$t('success.copied'))
      } else {
        window.ipc.send("COPY", value_to_copy)
        window.ipc.on("COPY", () => {
          this.copySuccess(this.$t('success.copied'))
        })
      }
    },
    
    copySuccess(message, password) {
      if (password) {
          this.loader_keys[password] = false 
          this.$forceUpdate()
      }
      this.$toast.success(message, {
          closeOnClick: true,
          timeout: 3000,
          icon: true
        })

        if (this.electron) {
          setTimeout(() => {
            window.ipc.send("COPY", "")
          }, 30000);
        }
    },

    copyPassword(key_id) {
      this.loader_keys[key_id] = true
      this.$forceUpdate()

      const uri = `/api/v1/key/${key_id}`

      http.get(uri).then((response) => {
        if (response.data.password.value) {
          if (!this.electron) {
            this.$copyText(response.data.password.value).then(() => {
              this.copySuccess(this.$t("success.password_copied"), key_id)
            })
          } else {
            window.ipc.send("COPY", response.data.password.value)
            window.ipc.on("COPY", () => {
              this.copySuccess(this.$t("success.password_copied"), key_id)
            })
          }
        } else {
          this.copySuccess(this.$t("success.password_copied"), key_id)
        }
      })    
    },

    addKey() {
      EventBus.$emit("editKey", null, this.current_folder)
    },

    editKey(item) {
      EventBus.$emit("editKey", item._id)
    },

    deleteItem(item) {
      const callback = () =>{
        for (let i in this.keys) {
          if (this.keys[i]._id === item._id) {
            this.keys.splice(i, 1)
            break
          }
        }
        const msg = this.in_trash ? "success.key_deleted" : "success.key_moved_to_trash"
        this.$toast.success(this.$t(msg), {
          closeOnClick: true,
          timeout: 3000,
          icon: true
        })
      }
      if (!this.in_trash) http.post(`/api/v1/key/${item._id}/move`,this.trash._id).then(callback)
      else http.delete(`/api/v1/key/${item._id}`).then(callback);
    },

    startDrag(event) {
      sessionStorage.setItem("draggedKey", event.srcElement.id)
    },

    endDrag() {
      sessionStorage.removeItem("draggedKey")
    },
  }
})
</script>
<style>
.restore_folder{
  padding:5px;
  font-weight: bold;
  background-color: #DDB249;
  color: #FFFFFF !important;
  line-height: 1.5;
  font-size:16px;
}
</style>
