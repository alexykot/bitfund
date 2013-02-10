var jsdom  = require('jsdom');
var fs     = require('fs');
var jquery = require('jquery');
var jqplot = fs.readFileSync("/mnt/hgfs/Projects/BitFund/Sources/source/bitfund/static/js/jquery.jqplot.min.js").toString();

var Canvas = require('canvas')

jsdom.env({
   html: 'http://news.ycombinator.com/',
   src: [
      jquery
   ],
   done: function(errors, window) {
      var $ = window.$;
      console.log('HN Links');
      $('td.title:not(:last) a').each(function() {
         console.log(' -', $(this).text());
      });
   }
});