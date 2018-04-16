var img = new Image;
var iImage = 0;
var images = ['BryceCanyon.jpg'];

function redraw() {
    //var sel = document.getElementById('PicturesSelect');
    //sel.innerHTML = "";
    //for (var i = 0; i < images.length; i++) {
    //    var opt = document.createElement('option');
    //    opt.innerHTML = images[i];
    //    opt.value = images[i];
    //    sel.appendChild(opt);
    //}
    //sel.value = images[iImage];
}

function OnSelect(elem) {
    iImage = elem.selectedIndex;
    img.src = img.src = './img/' + images[iImage];
    redraw();
}

function OnPrevious() {
    iImage--
    if (iImage < 0)
        iImage = images.length - 1;
    img.src = img.src = './img/' + images[iImage];
    redraw();
}

function OnNext() {
    iImage++
    if (iImage >= images.length)
        iImage = 0
    img.src = img.src = './img/' + images[iImage];
    redraw();
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
    imgs = document.getElementById('slideshow').children;
    interval = 1000;
    severpic = 0
    currentPic = 0;
    imgs[currentPic].style.webkitAnimation = 'fadey ' + interval + 'ms';
    imgs[currentPic].style.animation = 'fadey ' + interval + 'ms';
    $.get("GetImages", function (serverImages) {
        var infiniteLoop = setInterval(function () {
            //imgs[currentPic].removeAttribute('style');
            //if (currentPic == imgs.length - 1) { currentPic = 0; } else { currentPic++; }
            if (severpic == serverImages.length - 1) { severpic = 0; } else { severpic++; }
            //imgs[currentPic].style.webkitAnimation = 'fadey ' + interval + 'ms';
            //imgs[currentPic].style.animation = 'fadey ' + interval + 'ms';
            
            imgs[currentPic].src = './img/' + serverImages[severpic];
            console.log(imgs[currentPic].src)
        }, interval);
    });
    
}
/*
window.onload = function () {
    img.src = './img/' + images[iImage];
    img.onload = function () {
        redraw();
    };

    $.get("GetImages", function (serverImages) {
        images = serverImages;
        iImage = 0;
        img.src = './img/' + images[iImage];
        redraw();

        imgs = document.getElementById('slideshow').children;
        imgs[0].src = './img/' + images[iImage];
        interval = 1000;
        currentPic = 0;
        imgs[0].style.webkitAnimation = 'fadey ' + interval + 'ms';
        imgs[0].style.animation = 'fadey ' + interval + 'ms';
        var infiniteLoop = setInterval(function () {
            imgs[0].removeAttribute('style');
            if (iImage == images.length - 1) { iImage = 0; } else { iImage++; }
            imgs[0].src = './img/' + images[iImage];
            imgs[0].style.webkitAnimation = 'fadey ' + interval + 'ms';
            imgs[0].style.animation = 'fadey ' + interval + 'ms';
        }, interval);
    });
}
*/