import axios from "axios"
import https from "https"
import router from "../router"
import EventBus from "@/event"
// create an axios instance

const service = axios.create({
    // timeout: 5000, // request timeout,
    httpsAgent: new https.Agent({
        rejectUnauthorized: false
    })
})

// request interceptor
service.interceptors.request.use(
    async (config) => {
        // do something before request is sent
        const token = sessionStorage.getItem("token")
        if (token) {
            // let each request carry token
            // ['X-Token'] is a custom headers key
            // please modify it according to the actual situation
            config.headers["Authorization"] = `Bearer ${token}`
        }

        const userAgent = navigator.userAgent.toLowerCase();
        const electron = userAgent.indexOf(" electron/") > -1
        if (electron) {
            config.baseURL = localStorage.getItem("teamlock_url")
        } else {
            config.baseURL = process.env.VUE_APP_BASE_URL
        }

        return config
    },
    (error) => {
        // do something with request error
        console.log(error) // for debug
        return Promise.reject(error)
    }
)

// response interceptor
service.interceptors.response.use(
    /**
     * If you want to get http information such as headers or status
     * Please return  response => response
    */

    /**
     * Determine the request status by custom code
     * Here is just an example
     * You can also judge the status by HTTP Status Code
     */
    (response) => {
        // if (response.status === 403) {
        //     sessionStorage.clear()
        //     sessionStorage.clear()
        //     this.$router.push("/login")
        //     location.reload()
        // } else {
        //     return response
        // }
        return response

        // const res = response.data

        // // if the custom code is not 20000, it is judged as an error.
        // if (res.code !== 20000) {
        //   Message({
        //     message: res.message || 'Error',
        //     type: 'error',
        //     duration: 5 * 1000
        //   })

        //   // 50008: Illegal token; 50012: Other clients logged in; 50014: Token expired;
        //   if (res.code === 50008 || res.code === 50012 || res.code === 50014) {
        //     // to re-login
        //     MessageBox.confirm('You have been logged out, you can cancel to stay on this page, or log in again', 'Confirm logout', {
        //       confirmButtonText: 'Re-Login',
        //       cancelButtonText: 'Cancel',
        //       type: 'warning'
        //     }).then(() => {
        //       store.dispatch('user/resetToken').then(() => {
        //         location.reload()
        //       })
        //     })
        //   }
        //   return Promise.reject(new Error(res.message || 'Error'))
        // } else {
        //   return res
        // }
    },
    (error) => {
        // console.error('err' + error) // for debug

        if (error.response) {
            if (error.response.status === 403) {
                sessionStorage.clear()
                EventBus.$emit("stopKeepAlive")
                if (window.location.hash !== "#/login") (
                    router.push({ name: "Login" })
                )
            }
        }

        throw error

        // if (error.response.status === 403) {
        //     // this.$router.push("/login")
        // } else if (error.response.status === 422) {
        //     console.error(error.response.data)
        //     // Message({
        //     //     type: "error",
        //     //     message: error.response.data.detail,
        //     //     duration: 10000
        //     // })
        // }
        // return Promise.reject(error)
    }
)

export default service