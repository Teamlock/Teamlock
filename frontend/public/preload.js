const { contextBridge, ipcRenderer } = require('electron');

const validChannels = ["GET_SETTINGS", "SET_SETTINGS", "COPY", "FINGERPRINT", "ENCRYPTED_PASSWORD", "DECRYPT", "DECRYPTED_PASSWORD", "ERROR_FINGERPRINT", "CAPABILITIES", "LOGOUT"];
contextBridge.exposeInMainWorld(
    'ipc', {
    send: (channel, data) => {
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    },
    on: (channel, func) => {
        if (validChannels.includes(channel)) {
            // Strip event as it includes `sender` and is a security risk
            ipcRenderer.on(channel, (event, ...args) => func(...args));
        }
    }
}
);