module.exports = {
    osxSign: {},
    osxNotarize: {
        tool: "notarytool",
        appleApiKey: `-----BEGIN PRIVATE KEY-----
MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg2CvZ7N4QLo9CJMz1
z6UzANWOimOikZdCHyAftLOtbvSgCgYIKoZIzj0DAQehRANCAAQGxJe4J7IszvRd
9JwIe14T6N706F7uZ5FVp5Zy9RMqkqSY7cGbDx3rg+C/PF7wcjnfhSj9a3aue8KE
sfg9JbT5
-----END PRIVATE KEY-----`,
        appleApiKeyId: "HK8Z9V7KJH",
        appleApiIssuer: "cb396ce3-18ef-4adf-a253-f3cf9d4e5f3d"
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