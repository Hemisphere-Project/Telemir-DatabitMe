

var osc = require('node-osc');

/** TELEMIR APP **/
var DEBUG = false;
var STATE = false;
var DEBUG_NOCTRL = false;
var TRIP_DURATION = 300;

///////////////////////////////////////////////
///////////////    DISPLAY MANAGER  ///////////
///////////////////////////////////////////////
var RESO = [[1920, 1080], [640, 480], [640, 480], [640, 480], [640, 480], [640, 480]];
var REMOTE_URL = 'http://telemir.fr/w/apps';

var win = require('./windows');
var DisplayManager = new win.WinManager(RESO, REMOTE_URL, DEBUG);

// Add SubApps
DisplayManager.add({ name: 'ticket', type : 'remote', screen: 0 });
DisplayManager.add({ name: 'telediv', type : 'remote', screen: 1,  width: 2, height: 2 });
DisplayManager.add({ name: 'prompterv2', type : 'remote', screen: 3, width: 1, height: 1 });

//DisplayManager.add({ name: 'console', screen: 5 });
//DisplayManager.add({ name: 'mire', type : 'remote', screen: 4 });
//DisplayManager.add({ name: 'average', screen: 0, width: 1 });
//DisplayManager.add({ name: 'mire', type : 'remote', screen: 3, width: 1, height: 1 });

///////////////////////////////////////////////
///////////////   PYTHON CONTROL CENTER  ///////////
///////////////////////////////////////////////
var PORT_PY_CTRL = 9010;
var pyCenter = new osc.Client('127.0.0.1', PORT_PY_CTRL);

///////////////////////////////////////////////
///////////////    MUSIC SOCKET  ///////////
///////////////////////////////////////////////
var PORT_OSC_MUSIC = 9007;
var musicCom = new osc.Client('192.168.0.101', PORT_OSC_MUSIC);


///////////////////////////////////////////////
///////////////    MUSIC SOCKET  ///////////
///////////////////////////////////////////////
var PORT_OSC_LIGHT = 3000;
var lightCom = new osc.Client('127.0.0.1', PORT_OSC_LIGHT);

///////////////////////////////////////////////
///////////////    WEBAPPS SOCKET   ///////////
///////////////////////////////////////////////
var CADENCY = 15000;
var PORT_WS = 8090;
var appscom = require('./appscom');
var appCom = new appscom.io(PORT_WS, CADENCY, musicCom);


///////////////////////////////////////////////
///////////////    CORPUS MANAGER    /////////
///////////////////////////////////////////////
var corpus = require('./corpus');
// var prompter = new corpus.Prompter(['ST_1.txt', 'IMG_1.txt', 'LIEUX.txt',
//     'INF.txt', 'IMG_2.txt', 'IMG_2.txt', 'INF.txt', 'LIEUX.txt', 'IMG_1.txt',
//     'ST_2.txt', 'ST_2.txt', 'IMG_1.txt', 'LIEUX.txt', 'INF.txt',
//     'IMG_2.txt', 'IMG_2.txt', 'INF.txt', 'LIEUX.txt', 'IMG_1.txt', 'ST_2.txt'], CADENCY, appCom);

var prompter = new corpus.Prompter(['ST_1.txt', 'IMG_1.txt', 'LIEUX.txt',
    'INF.txt', 'IMG_2.txt', 'ST_2.txt', 'AP.txt'], CADENCY, appCom);

///////////////////////////////////////////////
///////////////    HPLAYERZ        ///////////
///////////////////////////////////////////////
var PORT_OSC_HPLAYER = 9000;

var hplayer2 = new osc.Client('192.168.0.32', PORT_OSC_HPLAYER);
//var hplayer3 = new osc.Client('192.168.0.33', PORT_OSC_HPLAYER);
var hplayer4 = new osc.Client('192.168.0.34', PORT_OSC_HPLAYER);
var hplayer5 = new osc.Client('192.168.0.35', PORT_OSC_HPLAYER);
var hplayer6 = new osc.Client('192.168.0.36', PORT_OSC_HPLAYER);
var hplayer7 = new osc.Client('192.168.0.37', PORT_OSC_HPLAYER);


///////////////////////////////////////////////
/////////////// APP CONTROL           /////////
///////////////////////////////////////////////
function AppCtrl(duration) {
  this.running = false;
  this.lifelevel = 0;
  this.count = 0;
  this.beattime = 2000;
  this.triplength = duration*1000;
  this.startDiff = null;

  var that = this;
  this.heartbeater = setInterval( function() {
    that.count++;
    // IceBreaker
    if (that.lifelevel > 0) that.lifelevel--;
    else if (that.running) {
      console.log('Life level too low.. No Heartbeat received from EEG.. stopping apps !');
      that.stop();
    }
    // Trip end
    // console.log(that.count);
    // console.log(that.triplength/that.beattime);
    if (that.count >= (that.triplength/that.beattime) && that.running) {
      console.log('TRIP END ! Goodbye..');
      that.stop();
      DEBUG_NOCTRL = false;
    }
  }, this.beattime);

  this.calib = function() {
    this.stop();
    lightCom.send('/calib');
    appCom.send('calib');
  }

  this.start = function() {
    if (this.running) return;
    this.running = true;
    appCom.send('start');
    musicCom.send('/start');
    lightCom.send('/start');
    prompter.start();

    this.startDiff = setTimeout(function() {
      hplayer2.send('/play','/home/pi/media/biblio.mp4');
      //hplayer3.send('/play','/home/pi/media/statement.mp4');
      hplayer4.send('/play','/home/pi/media/navigation.mp4');
      hplayer5.send('/play','/home/pi/media/mediation.mp4');
      hplayer6.send('/play','/home/pi/media/statement.mp4');
      hplayer7.send('/play','/home/pi/media/abecedaire.mp4');
      that.startDiff = null;
    }, 30000);


    this.lifelevel = 2;
    this.count = 0;
    console.log('START');
  }

  this.stop = function() {
    if (!this.running) return;
    this.running = false;

    if (this.startDiff != null) {
      clearTimeout(this.startDiff);
      this.startDiff = null;
    }

    appCom.send('stop');
    musicCom.send('/stop');
    lightCom.send('/stop');
    prompter.stop();

    hplayer2.send('/stop');
    //hplayer3.send('/stop');
    hplayer4.send('/stop');
    hplayer5.send('/stop');
    hplayer6.send('/stop');
    hplayer7.send('/stop');

    pyCenter.send('/stop');

    console.log('STOP');
  }

  this.eegAlive = function() {
    this.lifelevel = 2;
    if (DEBUG_NOCTRL) if (!this.running && this.count>2) this.start();
  }
}

var AppControl = new AppCtrl(TRIP_DURATION);


///////////////////////////////////////////////
///////////////  EEG RECEIVER         /////////
///////////////////////////////////////////////
var PORT_OSC_PYACQ = 9001;
var PORT_OSC_PYCMD = 9009;

var eegServer = new osc.Server(PORT_OSC_PYACQ, '0.0.0.0');
var cmdServer = new osc.Server(PORT_OSC_PYCMD, '0.0.0.0');

// CMD Packet Received
cmdServer.on("message", function (msg, rinfo) {

  // START / STOP
  if (msg[1] == '/start') AppControl.start();
  else if (msg[1] == '/stop') AppControl.stop();
  else if (msg[1] == '/calib') AppControl.calib();

  console.log(msg);

});

// EEG Packet Received
eegServer.on("message", function (msg, rinfo) {

  AppControl.eegAlive();

  // EEG DATA
  if (msg[0] == '/EEGfeat') {
    // Repack bundle
    var bundle = { alpha: msg[1], blink: msg[2], tension: msg[3], beta: msg[4],
      teta: msg[5], mu: msg[6], ftheta: msg[7], engage: msg[8], coreldg: msg[9], crisp: msg[10] };

    prompter.push(bundle);
    appCom.send('oscdata', bundle);
    msgS = msg.slice();
    musicCom.send(msgS.shift(), msgS);
    msgS = msg.slice();
    lightCom.send(msgS.shift(), msgS);
  }

});




///////////////////////////////////////////////
///////////////    MAIN APP         ///////////
///////////////////////////////////////////////
var app = require('app');  // Module to control application life.

// Report crashes to our server.
if (DEBUG) require('crash-reporter').start();

// Quit when all windows are closed.
app.on('window-all-closed', function() { app.quit(); });

// This method will be called when Electron has done everything
app.on('ready', function() { DisplayManager.start(); });
