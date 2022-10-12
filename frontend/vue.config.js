module.exports = {
  assetsDir: 'static',
  transpileDependencies: [
    'vuetify'
  ],
  pluginOptions: {
    electronBuilder: {
      builderOptions: {
        productName: "Teamlock",
        appId: "io.teamlock.app",
        nsis: {
          // installerIcon: "public/icon.ico",
          // uninstallerIcon: "public/icon.ico"
        },
        mac: {
          icon: "public/appstore.png"
        },
        win: {
            icon: "public/appstore.png"
        }
      },
      // builderOptions: {
      //   // options placed here will be merged with default configuration and passed to electron-builder
      //   asar: false
      // }
    }
  }
}
