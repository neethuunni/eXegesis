const express = require('express');
const bodyParser = require('body-parser');
const xml = require('xml');
const app = express()

app.use(express.static(__dirname + '/public'));
app.use(bodyParser.json());


app.get('/xml', function(req, res) {
	const xmls  = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>"
	res.send(xml(xmls));

});

app.listen(process.env.PORT || 4040);
console.log('app is running on PORT 4040');
