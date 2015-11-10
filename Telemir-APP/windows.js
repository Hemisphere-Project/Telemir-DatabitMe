var BrowserWindow = require('browser-window');  // Module to create native browser window.

module.exports = {

  WinManager : function(RESO,REMOTE_URL,DEBUG) {

    this.start = function() {

    }

    function SubApp(params ) {
      var that = this;

      // DEFAULT SETTINGS
      this.name = null;
      this.type = 'local';
      this.screen = 0;
      this.width = 1;
      this.height = 1;
      this.bounds = {x:0, y:0, width:0, height:RESO[1][1]};
      this.url = null;

      // RETRIEVE SUPPLIED SETTINGS
      if (typeof params !== 'undefined')
        for (var property in params) this[property] = params[property];

      // MAKE BOUNDS
      // Horizontal Position
      if (this.screen > 0) this.bounds.x = RESO[0][0];
      for (var i=1; i<this.screen; i++) this.bounds.x += RESO[i][0];
      // Width
      if (this.screen == 0) this.bounds.width = 500;
      else for (var i=this.screen; i<(this.screen+this.width); i++) this.bounds.width += RESO[i][0];
      // Height
      if (this.screen > 0) this.bounds.height = RESO[this.screen][1] * this.height;

      // MAKE URL
      if (this.type == 'local') this.url = 'file://' + __dirname + '/apps/' + this.name + '/index.html';
      else if (this.type == 'url') this.url = this.name;
      else this.url = REMOTE_URL + '/' + this.name + '/';

      this.start = function() {
        this.stop();
        this.window = new BrowserWindow({frame: (this.screen == 0)});
        this.window.setBounds(this.bounds);
        this.window.loadUrl(this.url);
        //this.window.on('closed', function() { that.start();  }); //auto respawn
        if (DEBUG) this.window.openDevTools();
      };

      this.stop = function() {
        if (typeof this.window !== 'undefined') this.window.close();
        delete this.window;
      };

    };

    var that = this;
    this.subapps = [];

    this.add = function(params) {
      if (params.name !== null) this.subapps.push( new SubApp(params) );
      else console.log("Can't create empty app");
    };

    this.getByIndex = function(sel) {
      if (typeof sel === 'undefined') return this.subapps;
      else if (this.subapps[sel] !== 'undefined') return [this.subapps[sel]];
      else return [];
    }

    this.start = function(select) {
      var that = this;
      // Create the main window.
      // this.MainWin = new BrowserWindow({width: 500, height: 500, frame: false});
      // this.MainWin.setPosition(20, 20);
      // this.MainWin.loadUrl('file://' + __dirname + '/index.html');
      // this.MainWin.on('closed', function() {
      //   that.MainWin=null;
      //   that.stop();
      //   //app.quit();
      // });
      // MainWin.on('move', function(e) { console.log(MainWin.getBounds()); });
      //if (DEBUG) MainWin.openDevTools();

      this.getByIndex(select).forEach(function(app){ app.start() });
    };

    this.stop = function(select) {
      this.getByIndex(select).forEach(function(app){ app.stop() });
    };

  }

}
