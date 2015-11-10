var SocketIO = require('socket.io');
var fs = require("fs");
var exec = require('child_process').exec;

module.exports = {

  io: function(PORT_WS, CADENCY, musicSend) {
    var that = this;
    // SocketIO websocket
    this.ws = new SocketIO();
    this.ws.listen(PORT_WS);
    this.musicOsc = musicSend;
    this.count = 0;

    // onConnection event
    this.ws.on('connection', function(client) {
      client.on('disconnect', function(){ });
      client.on('hello', function(){  });
      client.on('AnimGlyphOK', function(phrase){
        if (phrase && 0 !== phrase.length) {
          client.broadcast.emit('phrase_step2', [phrase, CADENCY]);
          console.log([phrase, CADENCY]);
        }
      });
      client.on('POP', function(){
        that.musicOsc.send('/POP',1);
      });
      client.on('new_print', function(img){
        that.count++;
        var base64Data = img.replace(/^data:image\/png;base64,/, "");
        var file = "C:\\Users\\mgr\\Desktop\\TICKETS\\out"+that.count+".png";
        fs.writeFile(file, base64Data, 'base64', function(err) {
          var cmd = '"C:\\Program Files\\IrfanView\\i_view64.exe" '+file+' /print';
          exec(cmd, function(error, stdout, stderr) {
              console.log('stdout: ' + stdout);
              console.log('stderr: ' + stderr);
              if (error !== null) {
                  console.log('exec error: ' + error);
              }
          });
        });

      });
    });

    this.send = function(key,val) { that.ws.emit(key,val); }
  }
}
