<template>
  <span>
    <v-btn
      @click="revealPassword(item._id, field)"
      small
      icon
    >
      <v-icon small>mdi-eye</v-icon>
    </v-btn>
    <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <span 
          class="cursor"
          v-on:click.stop
          v-on:dblclick.stop="copySecret(item._id, field)"
          v-bind="attrs"
          v-on="on"
        >
          <span v-if="!is_loading && !revealed_password">
            *********
          </span>
          <span v-else-if="revealed_password">
            {{ revealed_password }}
          </span>
          <v-progress-circular v-else :width="2" :size="20" indeterminate color="primary"/>
        </span>
      </template>
      <span>{{ $t('tooltip.dblclick_copy') }}</span>
    </v-tooltip>
  </span>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import secretMixin from "@/mixins/secrets"
import renderMixin from "@/mixins/render"
import http from "@/utils/http"

export default defineComponent({
  mixins: [secretMixin, renderMixin],

  props: {
    item: {
      type: Object,
      required: true
    },

    category: {
      type: String,
      required: true
    },

    field: {
      type: String,
      required: true
    }
  },

  data: () => ({
    is_loading_reveal: false,
    revealed_password: "",
    is_loading: false
  }),

  methods: {
    async fetchSecret(secret_id, field) {
      const uri = `/api/v1/secret/${secret_id}`

      const { data } = await http.get(uri)
      return data[field].value
    },

    async revealPassword(secret_id, field) {
      this.is_loading = true
      const secret_value = await this.fetchSecret(secret_id, field);
      this.revealed_password = secret_value;
      this.is_loading = false

      setTimeout(() => {
        this.revealed_password = ""
      }, 5000);
    },

    async copySecret(secret_id, field) {
      this.is_loading = true
      this.$forceUpdate()
      const secret_value = await this.fetchSecret(secret_id, field)
      if (!this.electron) {
        this.$copyText(secret_value)
          .then(() => {
            this.copySuccess(this.$t("success.secret_copied"), secret_id)
            this.is_loading = false
            this.$forceUpdate()
          }, () => {
            this.$toast.warning(this.$t("warning.secret_cannot_be_copied"))
            this.is_loading = false
          })
      } else {
        window.ipc.send("COPY", secret_value)
        window.ipc.on("COPY", () => {
          this.copySuccess(this.$t("success.secret_copied"), secret_id)
          this.is_loading = false
          this.$forceUpdate()
        })
      }
    },
  }
})
</script>
