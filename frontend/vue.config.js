module.exports = {
  assetsDir: 'static',
  transpileDependencies: [
    'vuetify'
  ],
  pluginOptions: {
    electronBuilder: {
      builderOptions: {
        productName: "Teamlock",
        appId: "teamlock.io",
        nsis: {
          // installerIcon: "public/icon.ico",
          // uninstallerIcon: "public/icon.ico"
        },
        mac: {
          // icon: "public/icon.ico"
        }
      },
      // builderOptions: {
      //   // options placed here will be merged with default configuration and passed to electron-builder
      //   asar: false
      // }
    }
  }
}
