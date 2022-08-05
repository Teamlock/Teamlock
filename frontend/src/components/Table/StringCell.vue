<template>
  <v-tooltip bottom v-model="tooltip_copy">
    <template v-slot:activator="{ on, attrs }">
      <span
        class="cursor"
        v-on:click.stop
        v-on:dblclick.stop="copyData(item[field].value)"
        v-bind="attrs"
        v-on="on"
      >
        {{ item[field].value }}
      </span>
    </template>
    <span v-html="tooltipHTML" />
  </v-tooltip>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import secretMixin from "@/mixins/secrets"
import renderMixin from "@/mixins/render"

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

  data: (vm) => ({
    tooltip_copy: false,
    tooltipHTML: vm.$t('tooltip.dblclick_copy')
  }),

  methods: {
    copySuccess() {
      setTimeout(() => {
        this.tooltipHTML = this.$t("help.copied")
        this.tooltip_copy = true

        setTimeout(() => {
          this.tooltip_copy = false

          setTimeout(() => {
            this.tooltipHTML = this.$t("tooltip.dblclick_copy")
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
