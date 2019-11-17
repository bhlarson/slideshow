'use strict';
console.log("Starting Web Slideshow server on " + process.platform + " with node version " + process.version);
require('dotenv').config({ path: './config.env' });
var express = require('express');
var app = express();

var http = require('http').Server(app);
const fs = require('fs');
var mysql = require('mysql');

var pool = mysql.createPool({
    connectionLimit: 10,
    host: process.env.dbhost,
    user: process.env.dbuser,
    //password: process.env.dbpass,
    database: process.env.dbname
});

var ioSocket;

var clinetPath = './img/';
var imgPath = './public/img';
var imageUrl = './img/';
var pathExist = fs.existsSync(imgPath)
var files = fs.readdirSync(imgPath);

function BuildImageList(imgPath, clientPath){
    var imFiles;
    if(fs.existsSync(imgPath)){
        var files = fs.readdirSync(imgPath);
        var imFiles = files.filter(function (file) {
            var match;
            match = file.match(/.*\.(jpg)/ig);
            if (!match)
                match = file.match(/.*\.(png)/ig);
            return match;
        });

        imFiles.forEach(function(imFile, i){
            imFiles[i] = clientPath+imFile;
        });
    }
    return imFiles;
}

var imFiles = BuildImageList(imgPath, clinetPath);

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

app.get('/GetMedia', function (req,res){
    GetEntries().then(function (dbentries) {
        res.send(dbentries);
    });
});


http.listen(port, function () {
    console.log("Listening on port " + port);
});

function CreateTables(db) {
    let addTable = "create table if not exists " + process.env.datatable + " ( \
    id int primary key auto_increment COMMENT 'Unique file id',\
    filename TEXT NULL DEFAULT NULL,\
    description TEXT NULL DEFAULT NULL COMMENT 'Description of file',\
    filetype TEXT NULL DEFAULT NULL COMMENT 'File extension',\
    filepath TEXT NULL DEFAULT NULL,\
    url TEXT NULL DEFAULT NULL COMMENT 'URL to file',\
    image LONGTEXT NULL DEFAULT NULL COMMENT 'File Details' COLLATE 'utf8mb4_bin',\
    objects LONGTEXT NULL DEFAULT NULL COMMENT 'Objects in file' COLLATE 'utf8mb4_bin')";

    db.query(addTable, function (err, results, fields) {
        if (err) {
            console.log(err.message);
        }
    });

    let addLog = "create table if not exists " + process.env.slidelog + " ( \
        time DATETIME NULL DEFAULT NULL, \
        event DOUBLE NULL DEFAULT NULL, \
        data LONGTEXT NULL DEFAULT NULL COLLATE 'utf8mb4_bin' )"

    db.query(addLog, function (err, results, fields) {
        if (err) {
            console.log(err.message);
        }
    });
}

function DBHeader(){
    return ['filename','filetype','filepath','url', 'display','image','objects'];
}

function ImageEntry(filename, extension, filepath,url, stats){
    var imageEntry = [filename, extension, filepath, url+filename, 1, '', ''];

    return imageEntry;
}

function BuildImageList01(imgPath, imArray, url){
    if(fs.existsSync(imgPath)){

        var files = fs.readdirSync(imgPath);
        for(var i=0; i<files.length; i++ ){
            var filePath = imgPath+'\\'+files[i];
            var stats = fs.statSync(filePath);
            if(stats.isDirectory())
            {
                BuildImageList01(filePath, imArray, url+files[i]);
            }
            else if(files[i].match(/.*\.(jpg)/ig)){
                var ent = ImageEntry(files[i], 'jpg', filePath, url);
                imArray.push(ent);
            }
            else if(files[i].match(/.*\.(png)/ig)) {
                var ent = ImageEntry(files[i], 'png', filePath, url);
                imArray.push(ent);
            }
        }
    }
}

function GetEntries() {
    return new Promise(function (resolve, reject) {
        var connectionString = 'SELECT * FROM `' + process.env.datatable +'`';
        pool.query(connectionString, function (dberr, dbres, dbfields) {
            if (dberr)
                reject(dberr);
            else {
                resolve(dbres);
            }
        });
    });
}

function AddImagesToDb(db, dbHeader, data){
    // This is failing to insert a set of images into the database.  Err in SQL syntax
    // Change from JSON to array with header defining columns: https://www.technicalkeeda.com/nodejs-tutorials/insert-multiple-records-into-mysql-using-nodejs
    var sql = 'INSERT INTO ' + process.env.datatable +' ('+dbHeader+ ') VALUES ?';
    db.query(sql, [data], function (dberr, dbres, dbfields) {
        console.log(dberr);
    });
}

function Initialize(){
    CreateTables(pool);

    if(true){
        var dbHeader = DBHeader();
        var dbData = [];
        BuildImageList01("C:\\Users\\brad.larson1\\Pictures", dbData, imageUrl);
        AddImagesToDb(pool, dbHeader, dbData);
    }

}

Initialize();
module.exports = app;
console.log("DeepArchive Started");