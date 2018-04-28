var img = new Image;
var iImage = 0;
var images = [];
severpic = 0;

function ShuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        let j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function redraw() {
    img.src = './img/' + images[severpic];
    img.style.maxWidth = screen.width + "px";
    img.style.maxHeight = screen.height + "px";

    link = document.getElementById("container");
    console.log('Screen:(' + screen.width + ',' + screen.height + '), img=(' + link.clientHeight + ',' + link.clientWidth + ')');
}

function OnSelect(elem) {
    if (elem >= 0 && elem < images.length) {
        severpic = elem;
        redraw();
    }
    iImage = elem.selectedIndex;
    img.src = img.src = './img/' + images[iImage];
    
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

var infiniteLoop = 0;
function StartInterval(interval = 3000) {
    if (infiniteLoop) {
        clearInterval(infiniteLoop);
        infiniteLoop = 0;
    }

    infiniteLoop = setInterval(function () {
        OnNext();
    }, interval);
}

function cancelFullScreen() {
    if (document.cancelFullScreen) {
        document.cancelFullScreen();
    } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
    } else if (document.webkitCancelFullScreen) {
        document.webkitCancelFullScreen();
    } else if (document.msCancelFullScreen) {
        document.msCancelFullScreen();
    }
    link = document.getElementById("container");
    link.removeAttribute("onclick");
    link.setAttribute("onclick", "fullScreen(this)");
}

function fullScreen(element) {
    if (element.requestFullScreen) {
        element.requestFullScreen();
    } else if (element.webkitRequestFullScreen) {
        element.webkitRequestFullScreen();
    } else if (element.mozRequestFullScreen) {
        element.mozRequestFullScreen();
    }
    link = document.getElementById("container");
    link.removeAttribute("onclick");
    link.setAttribute("onclick", "cancelFullScreen()");
}

window.onload = function () {
    img = document.getElementById('slideshow');
    
    currentPic = 0;

    $.get("GetImages", function (serverImages) {
        images = serverImages;
        ShuffleArray(images);
        StartInterval();
    });
    
}

document.onkeydown = function (e) {
    switch (e.keyCode) {
        case 37: // Left
        case 38: // Up
            OnPrevious();
            StartInterval();
            break;
        case 39: // Right
        case 40: // down
            OnNext();
            StartInterval();
            break;
    }
};
