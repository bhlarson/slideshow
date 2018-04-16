'use strict';
console.log("Starting DeepArchive on " + process.platform + " with node version " + process.version);
require('dotenv').config({ path: './config.env' });
var express = require('express');
var app = express();
var http = require('http').Server(app);
const fs = require('fs');
var io = require('socket.io')(http);
var ioSocket;

var clinetPath = '/img'
var imgPath = './public' + clinetPath;
var pathExist = fs.existsSync(imgPath)
var files = fs.readdirSync(imgPath);

var imFiles = files.filter(function (file) {
    var match;
    match = file.match(/.*\.(jpg)/ig);
    if (!match)
        match = file.match(/.*\.(png)/ig);
    return match;
});

for (var i in imFiles) {
    console.log('Image Loaded: ' + imFiles[i]);
}

// http communications
var port = Number(process.env.nodeport) || 1337;
app.use(express.static('public'));

app.get('/', function (req, res) {
    res.sendFile('index.html');
});

app.get('/GetImages', function (req, res) {
    res.send(imFiles);
});


http.listen(port, function () {
    console.log("Listening on port " + port);
});

// Establish sockit.io communications
io.on('connection', function (socket) {
    socket.broadcast.emit('Server Connected');
    ioSocket = socket;
    socket.on('disconnect', function () {
        console.log('Socket.IO  disconnected ' + socket.id);
    });
    socket.on('connect_failed', function () {
        console.log('socket.io connect_failed');
    })
    socket.on('reconnect_failed', function () {
        console.log('socket.io reconnect_failed');
    })
    socket.on('error', function (err) {
        console.log('socket.io error:' + err);
    })
    socket.on('Command', function (data) {
        console.log('Command ' + JSON.stringify(data));
    });
});

module.exports = app;
console.log("DeepArchive Started");
