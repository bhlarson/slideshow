var container = document.getElementById("container");
var canvas = d3.select(container).append("canvas");
var severpic = 0;
var iImage = 0;
var infiniteLoop = 0;
var images = [];

function ShuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
      let j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
  }
}

function loadImage(url, index, array) {
  return new Promise((resolve, reject) => {
      let img = new Image();
      img.addEventListener('load', e => resolve(img, index, array));
      img.addEventListener('error', () => {
          reject(new Error(`Failed to load image's URL: ${url}`));
      });
      img.src = url;
  });
}

async function asyncForEach(array, callback) {
  for (let index = 0; index < array.length; index++) {
      await callback(array[index], index, array);
  }
  return h + ":" + m + " " + ampm;
}

function LoadImages(url, index, numImages){
  return new Promise((resolve, reject) => {
      let img = new Image();
      img.addEventListener('load', e => {
          resolve(img, index);
      });
      img.addEventListener('error', () => {
          reject(new Error(`Failed to load image's URL: ${url}`));
      });
      img.src = url;
  });
}

async function AsyncLoadImages(array) {
  const asyncFunctions = []
  for (let index = 0; index < array.length; index++)
      asyncFunctions.push(LoadImages(array[index], index, array.length));

  images = await Promise.all(asyncFunctions);

  //ShuffleArray(images);
  StartInterval();
}

function OnPrevious() {
  if (severpic == 0)
  { severpic = images.length - 1; }
  else { severpic--; }

  redraw();
}

function OnNext() {
  if (severpic == images.length - 1)
  { severpic = 0; }
  else { severpic++; }

  redraw();
}

function StartInterval(interval = 5000) {

    // Draw for the first time to initialize.
    redraw();
    // Redraw based on the new size whenever the browser window is resized.
    window.addEventListener("resize", redraw);

    if (infiniteLoop) {
        clearInterval(infiniteLoop);
        infiniteLoop = 0;
    }

    infiniteLoop = setInterval(function () {
        OnNext();
    }, interval);
}

function redraw(){

  // Extract the width and height that was computed by CSS.
  var width = container.clientWidth;
  var height = container.clientHeight;

  console.log(width + 'x ' + height)

  canvas
    .attr("width", width)
    .attr("height", height);  

    var ctx = canvas.node().getContext("2d");
    img = images[severpic];

    var arx = img.width/width;
    var ary = img.height/height;

    var dx = 0;
    var dy = 0;
    var dw = width;
    var dh = height;
    if(arx > ary){
      dh = height * ary/arx
      dy = (height-dh)/2
    }
    else{
      dw = width * arx/ary
      dx = (width-dw)/2
    }

    ctx.drawImage(img,0,0,img.width,img.height,dx,dy,dw,dh);
}

window.onload = function () {
  currentPic = 0;

  url = document.URL + "GetImages";
  fetch(url)
      .then(response => response.json())
      .then(serverImages => {
          AsyncLoadImages(serverImages);
      })
      .catch(function (error) {
          console.log(error)
      });
  
}
