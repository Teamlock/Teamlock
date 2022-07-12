import settings from 'electron-settings';
import { clipboard } from 'electron';

const ipc = {
    init: (ipcMain) => {
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
        })
    }
}

export default ipc