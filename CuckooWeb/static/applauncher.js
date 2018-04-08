/**
 * Application launcher.
 */

// start app function
function startApp() {
    // initialise the application
    myapp.init({
        "containerDivId": "dwv",
        "fitToWindow": true,
        "gui": ["tool","load", "undo"],
        "loaders": ["Url"],
        "tools": ["Scroll", "ZoomAndPan", "WindowLevel", "Draw"],
        "shapes": ["Arrow", "Ruler", "Protractor", "Rectangle", "Roi", "Ellipse", "FreeHand"],
        "isMobile": false
    });
    // file = document.getElementById('file-input')
    // if (file) {
    //     file.addEventListener('change', readSingleFile, false);
    //     // alert("success")
    // }
    // else
    //     alert("faild")
    var size = dwv.gui.getWindowSize();
    $(".layerContainer").height(size.height);
    dwv.gui.appendResetHtml(myapp);
    
    var layerCon = document.getElementsByClassName("layerContainer")[0]
    var urlroot1 = layerCon.getAttribute("urlroot");
    var fileNames = files1;    
    imageUrl = []
    for (i in fileNames)
        imageUrl.push(urlroot1+fileNames[i])
    myapp.loadURLs(imageUrl);
    // myapp.loadFiles(["1_2_840_113619_2_98_6140_1425970638_0_16_64.dcm"])
    //http://127.0.0.1:5000/1.dcm
}

// function readSingleFile(e) {
//     myapp.loadFiles(e.target.files)

// }
// Image decoders (for web workers)
dwv.image.decoderScripts = {
    "jpeg2000": "../../decoders/pdfjs/decode-jpeg2000.js",
    "jpeg-lossless": "../../decoders/rii-mango/decode-jpegloss.js",
    "jpeg-baseline": "../../decoders/pdfjs/decode-jpegbaseline.js"
};
// main application
var myapp = new dwv.App();
// status flags
var domContentLoaded = false;
var i18nInitialised = false;
// launch when both DOM and i18n are ready
function launchApp() {
    if (domContentLoaded && i18nInitialised) {
        startApp();
    }
}
// i18n ready?
dwv.i18nOnInitialised(function () {
    i18nInitialised = true;
    launchApp();
});



// check browser support
dwv.browser.check();
// initialise i18n
dwv.i18nInitialise();

// DOM ready?
document.addEventListener("DOMContentLoaded", function (/*event*/) {
    domContentLoaded = true;
    launchApp();
});
// document.getElementById('file-input')
//     .addEventListener('change', readSingleFile, false);
