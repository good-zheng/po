export default defineAppConfig({
  lazyCodeLoading: 'requiredComponents',
  pages: ['pages/session/index', 'pages/mine/index', 'pages/login/index', 'pages/profile/edit', 'pages/history/index'],
  // 麦克风是本产品的入口能力：只在用户点「开始录音」后收音，仍必须在 app.json 里声明用途，
  // 否则微信不会弹授权框（也需在公众平台「隐私保护指引」里同步声明）
  permission: {
    'scope.record': {
      desc: '用于录制对方说的话并实时转写成文字',
    },
  },
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff',
    navigationBarTitleText: '言外',
    navigationBarTextStyle: 'black',
  },
  tabBar: {
    color: '#9a9aa2',
    selectedColor: '#3b5bdb',
    backgroundColor: '#fcfcfd',
    borderStyle: 'black',
    list: [
      {
        pagePath: 'pages/session/index',
        text: '会话',
        iconPath: 'assets/icons/tab-session.png',
        selectedIconPath: 'assets/icons/tab-session-active.png',
      },
      {
        pagePath: 'pages/mine/index',
        text: '我的',
        iconPath: 'assets/icons/tab-mine.png',
        selectedIconPath: 'assets/icons/tab-mine-active.png',
      },
    ],
  },
});
