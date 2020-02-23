var motors;
var groups;
var media;

function AppendMedia(row, entry) {
    // Clear out the row if it already exists
    while (row.cells && row.cells.length > 0) {
        row.deleteCell(row.cells.length - 1);
    }

    const iFilename = 0;
    const iFileType = 1;
    const iFilePath = 2;
    const iURL = 3;
    const iDisplay = 4;

    var cellFilename = row.insertCell(iFilename);
    var cellFileType = row.insertCell(iFileType);
    var cellFilePath = row.insertCell(iFilePath);
    var cellURL = row.insertCell(iURL);
    var cellDisplay = row.insertCell(iDisplay);

    if (typeof entry === 'undefined' || entry === null) {
        entry = { filename: '', filetype: '', filepath: '', url: '', display: false };
    }

    cellFilename.appendChild(document.createTextNode(entry.filename));
    cellFileType.appendChild(document.createTextNode(entry.filetype));
    cellFilePath.appendChild(document.createTextNode(entry.filepath));

    // Create anchor element. 
    var a = document.createElement('a');
    var link = document.createTextNode(entry.url); 
    a.appendChild(link);  
    a.href = entry.url;
    cellURL.appendChild(a);

    var display = document.createElement("INPUT");
    display.setAttribute("type", "checkbox");
    display.checked = entry.display;
    display.addEventListener("click", function () {
        entry.display = display.checked;
    }, false);
    cellDisplay.appendChild(display)
}

function AddDeviceSelect(deviceNames, value) {
    var devices = document.createElement("select");
    //Create and append the options
    for (var i = 0; i < deviceNames.length; i++) {
        var option = document.createElement("option");
        option.id = "DeviceSelect";
        option.value = deviceNames[i];
        option.text = deviceNames[i];
        devices.appendChild(option);
    }
    if (value) {
        devices.value = value;
    }
    return devices;
}


function UpdateMedia(media) {
    var mediaTable = document.getElementById("mediaTable");

    if (media && media.constructor === Array) {
        media.forEach(function (entry, i) {
            var row = mediaTable.insertRow(i + 1);
            AppendMedia(row, entry);
        });
    }
}

window.onload = function () {
    media_url = window.location.origin + "/GetMediaList";
    fetch(media_url).then((response) => response.json()).then(in_media => {
        media = in_media;
        UpdateMedia(media)
    }
    ).catch(function (error) {
        console.log(error)
    });
}