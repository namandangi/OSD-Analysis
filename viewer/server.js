//"use strict";
const path = require("path");



const express = require("express");
var livereload = require("livereload");
var connectLiveReload = require("connect-livereload");

const liveReloadServer = livereload.createServer();
liveReloadServer.server.once("connection", () => {
  setTimeout(() => {
    liveReloadServer.refresh("/");
  }, 100);
});

liveReloadServer.watch(__dirname);

// Constants
const PORT = 3001;
const HOST = "0.0.0.0";

// App
const app = express();

app.use(connectLiveReload());

app.get("/", (req, res) => {
  //get requests to the root ("/") will route here
  res.sendFile("index.html", { root: __dirname }); //server responds by sending the index.html file to the client's browser
  //the .sendFile method needs the absolute path to the file, see: https://expressjs.com/en/4x/api.html#res.sendFile
});

app.use(express.static("static"));
app.use("/node_modules", express.static("node_modules"));

app.listen(PORT, HOST);
console.log(`Running on http://${HOST}:${PORT}`);
