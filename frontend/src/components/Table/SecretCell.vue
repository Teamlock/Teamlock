<template>
  <span>
    <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <span 
          class="cursor"
          v-on:click.stop
          v-on:dblclick.stop="copySecret(item._id, field)"
          v-bind="attrs"
          v-on="on"
        >
          <span v-if="!is_loading">
            *********
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
    is_loading: false
  }),

  methods: {
    copySecret(secret_id, field) {
      this.is_loading = true
      this.$forceUpdate()

      const uri = `/api/v1/secret/${secret_id}`

      http.get(uri).then((response) => {
        if (response.data[field].value) {
          if (!this.electron) {
            this.$copyText(response.data[field].value).then(() => {
              this.copySuccess(this.$t("success.secret_copied"), secret_id)
              this.is_loading = false
              this.$forceUpdate()
            })
          } else {
            window.ipc.send("COPY", response.data[field].value)
            window.ipc.on("COPY", () => {
              this.copySuccess(this.$t("success.secret_copied"), secret_id)
              this.is_loading = false
              this.$forceUpdate()
            })
          }
        } else {
          this.copySuccess(this.$t("success.secret_copied"), secret_id)
          this.is_loading = false
          this.$forceUpdate()
        }
      })
    },
  }
})
</script>
