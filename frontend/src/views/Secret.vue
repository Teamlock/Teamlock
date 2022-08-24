<template>
  <span v-if="selected_workspace" @click.stop>
    <v-data-table
        hide-default-footer
        :headers="headers"
        :loading="loading"
        class="elevation-1"
        fill-height
        :items="secrets"
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
          @click="addSecret(category, current_folder)"
          style="float: right"
          v-if="!in_trash && (selected_workspace.owner === user._id || selected_workspace.can_write)"
        >
          <v-icon small>mdi-plus</v-icon>
          {{ $t("button.add") }}
        </v-btn>     
      </template>
      <template v-slot:item="{ item,index }">
        <td class="restore_folder" colspan="6" v-if="index == 0 && in_trash">
          <v-icon small>mdi-alert</v-icon>
          {{$t("warning.restore")}}
        </td>
        <draggable
          :list="secrets"
          tag="tr"
          @start="startDrag"
          @end="endDrag"
          class="text-left"
          :key="item._id"
          :id="item._id"
          v-if="headers"
        >
          <td
            v-for="header, i in headers"
            :key="i"
          >
            <span v-if="header.component === 'SecretCell'">
              <secret-cell
                :category="category"
                :field="header.value"
                :item="item"
              />
            </span>
            <span v-else-if="header.component === 'UrlCell'">
              <url-cell
                :category="category"
                :field="header.value"
                :item="item"
              />
            </span>
            <span v-else-if="header.component === 'ActionCell'">
              <action-cell
                :can_share_external="can_share_external"
                :category="category"
                :item="item"
                @delete="deleteItem"
              />
            </span>
            <span v-else>
              <string-cell
                :category="category"
                :field="header.value"
                :item="item"
              />
            </span>
          </td>
        </draggable>
      </template>
    </v-data-table>
  </span>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import secretMixin from "@/mixins/secrets"
import renderMixin from "@/mixins/render"
import draggable from 'vuedraggable'
import { mapGetters } from 'vuex'
import http from "@/utils/http"
import EventBus from "@/event"
import StringCell from '../components/Table/StringCell.vue'
import SecretCell from '../components/Table/SecretCell.vue'
import ActionCell from '../components/Table/ActionCell.vue'
import UrlCell from '../components/Table/UrlCell.vue'

export default defineComponent({
  components: {
    draggable,
    StringCell,
    SecretCell,
    ActionCell,
    UrlCell
  },

  mixins: [secretMixin, renderMixin],

  props: {
    category: {
      type: String,
      required: true
    }
  },

  data: () => ({
    can_share_external: false,
    loading: false,
    loader_secrets: {},
    is_pro: false,
    headers: [],
    secrets: []
  }),

  computed: {
    ...mapGetters({
      user: 'getUser',
      twilioEnabled: 'getTwilio',
      current_folder: 'getFolder',
      selected_workspace: "getWorkspace"
    }),

    height() {
      const height = document.getElementsByClassName("v-main__wrap")[0].offsetHeight;
      return height - 45
    }
  },

  watch: {},

  beforeMount() {
    let middleHeader = null
    switch(this.category) {
      case "login":
        middleHeader = this.login.headers;
        break;
      case "server":
        middleHeader = this.server.headers;
        break
      case "phone":
        middleHeader = this.phone.headers;
        break
      case "bank":
        middleHeader = this.bank.headers;
        break
    }

    let headers = [this.startHeader].concat(middleHeader)
    headers.push(this.endHeader)
    this.headers = headers

    this.is_pro = this.$store.state.pro
  },

  mounted() {
    EventBus.$on("refreshSecrets", () => {
      this.getSecrets()
    })

    EventBus.$on("searchSecrets", (search) => {
      this.searchSecrets(search)
    })

    EventBus.$on("folder_trash", res =>{
      this.in_trash = res.in_trash;
      this.is_trash = res.is_trash;
      if(res.is_trash) this.in_trash = true;
    })

    EventBus.$on("empty_trash",() => this.emptyTrash());
  },

  methods: {
    addSecret(secret_type, folder) {
      EventBus.$emit(`edit_${secret_type}`, null, folder)
    },

    emptyTrash(){
      this.loading = true;
      const uri = `/api/v1/workspace/${sessionStorage.getItem("current_workspace")}/trash`;
      http.delete(uri).then(() =>{
        this.secrets = [];
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
    searchSecrets(search) {
      this.loading = true;
      this.secrets = []

      const uri = "/api/v1/secret/search"
      const params = {
        search: search,
        workspace: this.selected_workspace._id
      }

      http.get(uri, {params: params}).then((response) => {
        this.secrets = response.data;
        this.loading = false
      })
    },

    getSecrets() {
      if (!this.current_folder) return

      http.get(`/api/v1/workspace/${sessionStorage.getItem("current_workspace")}/trash`)
        .then(response => this.trash = response.data)

      if (this.selected_workspace.owner  === this.$store.state.user._id) {
        this.can_share_external = true
      } else {
        this.can_share_external = this.selected_workspace.can_share_external
      }

      this.loading = true;
      this.secrets = [];

      const params = {
        params: {
          category: this.category
        }
      }

      const uri = `/api/v1/folder/${this.current_folder}/secrets`
      http.get(uri, params).then((response) => {
        this.secrets = response.data
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
    deleteItem(item) {
      const callback = () => {
        for (let i in this.secrets) {
          if (this.secrets[i]._id === item._id) {
            this.secrets.splice(i, 1)
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
      if (!this.in_trash) http.post(`/api/v1/secret/${item._id}/move`, this.trash._id).then(callback)
      else http.delete(`/api/v1/secret/${item._id}`).then(callback);
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