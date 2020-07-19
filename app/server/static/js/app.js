const init = () => {
    var router = new Router([
        new Route('home', './home.html', true),            
        new Route('app', './app.html')
    ]);
}
init();

const ObjectLength = ( object ) => {
    var length = 0;
    for( var key in object ) {
        if( object.hasOwnProperty(key) ) {
            ++length;
        }
    }
    return length;
};

const send_file = () => {
    const formData = new FormData();
    const chatId = document.getElementById("chat_id").value;
    const fileElement = document.getElementById("file_id");
    const request = new XMLHttpRequest();

    if (chatId === "" && chatId.length <= 5){
        alert("Provide a valid chat_id to save a file !")
    }else{
        document.getElementById("response").innerHTML = "Sending the file..."
        formData.append("chat_id", chatId);
        // HTML file input, chosen by user
        formData.append("file", fileElement.files[0]);
        request.open("POST", "/api/upload");
        request.onload  = function() {
            console.log("[+] res: ", request.response);
            const responseHtml = `
                    <b>- File-name :</b> <i style="color: #0069ff;">${JSON.parse(request.response)["json_map"]["file"]["file_name"]}</i>
                    <br/><b>- File-key :</b> <i style="color: red;">${JSON.parse(request.response)["file_key"]}</i>
                    <br/><b>- Chunks :</b> ${ObjectLength(JSON.parse(request.response)["json_map"]["file_map"])}
                    <br/><b>- Timestamp :</b> ${new Date().toUTCString()} <br/>`;
            if (ObjectLength(JSON.parse(request.response)["json_map"]["file_map"]) <= 0){
                document.getElementById("response").innerHTML = "<i style='color: red;'>Something went wrong, please check your chat-id</i>";
            }else{
                document.getElementById("response").innerHTML = responseHtml;
            }
            // do something with jsonResponse
         };
        request.send(formData);
    }
}

const get_file = () => {
    const fileKey = document.getElementById("file_key").value;
    const request = new XMLHttpRequest();
    if (fileKey === "" && fileKey.length <= 20){
        alert("Provide a file_key to get a download file link !")
    }else{
        document.getElementById("response2").innerHTML = "Generating the file..."
        request.open("GET", "/api/download/"+ fileKey);
        request.onload  = function() {
            console.log("[+] res: ", request.response);
            const responseHtml = `
                    <br/><b>- File-key :</b> <i style="color: red;">${JSON.parse(request.response)["file_key"]}</i>
                    <br/><b>- Download-link :</b> <a href='${JSON.parse(request.response)["download_link"]}' target='_blank'>Click here to download the file</a>
                    <br/><b>- Node :</b>'All files are deleted 24 hours after creating their download link.'`;
            if (typeof JSON.parse(request.response)["download_link"] === "undefined"){
                document.getElementById("response2").innerHTML = "<i style='color: red;'>Something went wrong, please check your file-key.</i>";
            }else{
                document.getElementById("response2").innerHTML = responseHtml;
            }
        }
        request.send(null);
    }
}