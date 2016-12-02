const Svg = require('svgutils').Svg;
const util = require('util');
const fs = require('fs');



// Svg.fromSvgDocument(__dirname + '/svg.svg', function(err, svg){
//   if (!err) {
//     console.log('success');
//   }
//   const json = svg.toJSON();
//   console.log(util.inspect(json['elements'][0]['bbox']));
// });

const parseString = require('xml2js').parseString;
const xml2js = require('xml2js');
var builder = new xml2js.Builder();


const xml = fs.readFileSync(__dirname + '/sign-up.svg');
// console.log(xml);
// parseString(xml, function (err, result) {
//     console.dir(result['svg']['g'][0]['g'][0]['text'][0]['tspan']);
// });
parseString(xml, function (err, result) {
    // console.log(result['svg']['g'][0]['g'][0]['g'][0]['text'][0]['tspan']);
    var xml = builder.buildObject(result);
    console.log(xml);
});

// var xml = "<superroot><root id=\"id\">Hello xml2js!</root></superroot>"
// parseString(xml, function (err, result) {
//     // console.dir(result);
    
//   });

// var obj = {name: "Super", Surname: "Man", age: 23};


