import { clipboard, safeStorage, systemPreferences } from 'electron';
import settings from 'electron-settings';

const ipc = {
    init: (ipcMain, win, app) => {
        ipcMain.on('GET_SETTINGS', async (event) => {
            const teamlock_settings = await settings.get("teamlock.settings")
            event.reply('GET_SETTINGS', teamlock_settings);
        });

        ipcMain.on("SET_SETTINGS", async (event, teamlock_settings) => {
            await settings.set("teamlock.settings", teamlock_settings)
        });

        ipcMain.on("COPY", (event, data) => {
            clipboard.writeText(data)
            if (data !== "") {
                event.reply("COPY")
            }
        }),

        ipcMain.on("FINGERPRINT", async (event, data) => {
            systemPreferences.promptTouchID("Teamlock need consent to enable Biometric Authentication")
                .then((success) => {
                    const buffer = safeStorage.encryptString(data.password)
                    const msg = buffer.toString("base64")
                    event.reply("ENCRYPTED_PASSWORD", {data: msg})
                }).catch(() => {
                    event.reply("ERROR_FINGERPRINT")
                })
        }),

        ipcMain.on("DECRYPT", async (event, data) => {
            systemPreferences.promptTouchID("Teamlock need consent")
                .then((success) => {
                    const decrypted_password = safeStorage.decryptString(Buffer.from(data.password, "base64"))
                    event.reply("DECRYPTED_PASSWORD", {data: decrypted_password})
                })
                .catch(() => {
                    event.reply("ERROR_FINGERPRINT")
                })
        }),

        ipcMain.on("CAPABILITIES", (event) => {
            let touchID = false
            try {
                touchID = systemPreferences.canPromptTouchID()
            } catch(_) {}

            const capabilities = {
                touchID: touchID
            }

            event.reply("CAPABILITIES", capabilities)
        }),

        ipcMain.on("LOGOUT", () => {
            win.close()
            win.destroy()
            app.quit()
        })
    }
}

export default ipc