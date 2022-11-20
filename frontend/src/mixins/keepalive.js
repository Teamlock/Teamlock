import http from "@/utils/http"
import EventBus from "@/event"

const keepAliveMixin = {
    data: () => ({
        interval: null
    }),
    mounted() {
        this.setInterval()

        document.addEventListener('visibilitychange', this.visibilityChange, false);

        EventBus.$on("stopKeepAlive", () => {
            this.delInterval()
        })
    },

    destroy() {
        this.delInterval()
    },

    methods: {
        async testAuth() {
            await http.get("/api/v1/auth/me")
        },

        delInterval() {
            EventBus.$emit("delIntervalNotification")
            if (this.interval) {
                clearInterval(this.interval)
            }
        },
        setInterval() {
            this.testAuth()
            EventBus.$emit("intervalNotification")
            this.interval = setInterval(() => {
                this.testAuth()
            }, 10000)
        },

        visibilityChange() {
            if (document.hidden) {
                if (this.interval) {
                    this.delInterval()
                }
            } else {
                this.setInterval()
            }
        }
    }
}

export default keepAliveMixin