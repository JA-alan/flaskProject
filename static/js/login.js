function createXMLHttpRequest() {
    var xmlHttp;

    if (window.XMLHttpRequest) {
        xmlHttp = new XMLHttpRequest();

        if (xmlHttp.overrideMimeType)

            xmlHttp.overrideMimeType('text/xml');

    } else if (window.ActiveXObject) {
        try {
            xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");

        } catch (e) {
            try {
                xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");

            } catch (e) {
            }

        }

    }

    return xmlHttp;

}
