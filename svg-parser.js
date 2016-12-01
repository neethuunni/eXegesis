var parse = require('parse-svg-path')
var extract = require('extract-svg-path')
 
var path = extract(__dirname + '/test.svg')
var svg = parse(path)
console.log(svg)