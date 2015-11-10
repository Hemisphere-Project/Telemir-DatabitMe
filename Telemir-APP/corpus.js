var fs = require('fs');

module.exports = {

  Prompter: function(files, cadency, appCom) {
    this.datas = {};
    this.loop = null;
    this.cadency = cadency;
    this.stepCount=0;
    this.files = files;
    this.corpus = new Array();
    this.lastPhrase = '';
    this.appCom = appCom;

    // Load texts
    for (var i=0; i<files.length; i++)
      this.corpus[i] = fs.readFileSync('.\\texts\\'+files[i]).toString().split("\n");

    // start interval
    this.start = function() {
      this.stop();
      var that = this;

      for (var i=0; i<files.length; i++)
        this.corpus[i] = fs.readFileSync('.\\texts\\'+files[i]).toString().split("\n");

      this.loop = setInterval(function(){ that.pickText(); }, this.cadency);
      setTimeout(function(){ that.pickText(); }, 1500);
    }

    // stop interval
    this.stop = function() {
      if (this.loop != null) clearInterval(this.loop);
      this.loop = null;
      this.stepCount=0;
      this.lastPhrase = this.phraseInit;
    }

    this.push = function(data) {
      for (var k in data)
          if (data.hasOwnProperty(k))
          {
            if (!this.datas.hasOwnProperty(k)) this.datas[k] = new Array();
            this.datas[k].push(data[k]);
          }
    }

    this.average = function(key) {
      var avg = -1;
      if (this.datas.hasOwnProperty(key)) {
        var total = 0;
        for (var i = 0; i<this.datas[key].length; i++) total+=this.datas[key][i];
        if (this.datas[key].length > 0) avg = total/this.datas[key].length;
        this.datas = {};
      }
      return avg;
    }

    this.scale = function(value, in_min, in_max, out_min, out_max) {
      return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
    }

    this.alphaScale = function( val ){
      var equalRepart = val;
      if (val >= 0 && val < 10) equalRepart = this.scale(val,0,10,0,20);
      if (val >= 10 && val < 20) equalRepart = this.scale(val,10,20,20,40);
      if (val >= 20 && val < 30) equalRepart = this.scale(val,20,30,40,60);
      if (val >= 30 && val < 40) equalRepart = this.scale(val,30,40,60,80);
      if (val >= 40 && val < 100) equalRepart = this.scale(val,40,100,80,100);
      return equalRepart;
    }

    this.pickText = function() {
      var newText = '';

      var param = 'alpha';

      /*if (this.files[this.stepCount] == 'IMG_2.txt') param = 'alpha';
      else if (this.files[this.stepCount] == 'INF.txt') param = 'beta';
      else if (this.files[this.stepCount] == 'IMG_1.txt') param = 'ftheta';
      else if (this.files[this.stepCount] == 'ST_1.txt') param = 'crisp';
      else if (this.files[this.stepCount] == 'ST_2.txt') param = 'engage';
      else if (this.files[this.stepCount] == 'LIEUX.txt') param = 'alpha';
      else if (this.files[this.stepCount] == 'APP.txt') param = 'correldg';*/


      var avg = this.average(param);     // Moyenne du tableau alpha sur la derniere séquence
      if (avg < 0) return;
      if (param == 'alpha') avg = this.alphaScale(avg);   // Répartition non linéaire pour explorer ts les indexs
      var index = Math.floor( this.corpus[this.stepCount].length * avg / 100 ) ;  // index en fonction taille tableau texte

      console.log(param);
      console.log(avg);
      //if (this.stepCount == 0)

      newText = this.corpus[this.stepCount][index];
      this.corpus[this.stepCount].splice(index,1);
      this.stepCount = (this.stepCount+1) % this.corpus.length;

      if (newText && 0 !== newText.length) {
        this.lastPhrase = newText;
        this.appCom.send('phrase_step1', this.lastPhrase);
        console.log(this.lastPhrase);
      }
    }
  }

}
