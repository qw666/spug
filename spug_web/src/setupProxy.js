/**
 * Copyright (c) OpenSpug Organization. https://github.com/openspug/spug
 * Copyright (c) <spug.dev@gmail.com>
 * Released under the AGPL-3.0 License.
 */
const proxy = require('http-proxy-middleware');

module.exports = function (app) {
 /* 10.188.15.192:8780*/
  app.use(proxy('/api/', {
    target: 'http://10.188.15.56:8780/api',
    changeOrigin: true,
    ws: true,
    headers: {'X-Real-IP': '1.1.1.1'},
    pathRewrite: {
      '^/api': ''
    }
  }))
};
