module.exports = {
    osxSign: {},
    osxNotarize: {
        tool: "notarytool",
        appleApiKey: process.env.APPLE_API_KEY,
        appleApiKeyId: process.env.APPLE_API_KEY_ID,
        appleApiIssuer: process.env.APPLE_API_ISSUER
    },
    "packagerConfig": {
        "icon": "./src/assets/img/icons/1024x1024.png"
    },
    "makers": [
        {
          "name": "@electron-forge/maker-squirrel",
          "config": {
            "iconUrl": "./src/assets/img/icons/1024x1024.ico",
            "setupIcon": "./src/assets/img/icons/1024x1024.ico",
            "name": "teamlock"
          }
        },
        {
          "name": "@electron-forge/maker-deb",
          "config": {
            "options": {
              "icon": "./src/assets/img/icons/1024x1024.png"
            }
          }
        },
        {
          "name": "@electron-forge/maker-dmg",
          "config": {
            "icon": "./src/assets/img/icons/1024x1024.icns"
          }
        }
    ]
}