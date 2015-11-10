var webPage = require('webpage');
var page = webPage.create();

page.viewportSize = { width: 270, height: 20 };
page.open("http://telemir.fr/apps/printer/", function start(status) {
  page.render('test.png', {format: 'png', quality: '100'});
  phantom.exit();
});


/*

mgr@RAN C:\Users\mgr\Desktop\phantomjs-2.0.0-windows\bin
> phantomjs.exe E:\Documents\GitHub\Telemir-Electron\img-web.js

mgr@RAN C:\Program Files\IrfanView
> i_view64.exe C:\Users\mgr\Desktop\phantomjs-2.0.0-windows\bin\test.png /print

*/
