const init = () => {
    var router = new Router([
        new Route('home', './home.html', true),            
        new Route('app', './app.html')
    ]);
}
init();

const send_file = () => {
    const formData = new FormData();
    const chatId = document.getElementById("chat_id").value;
    const fileElement = document.getElementById("file_id");
    const request = new XMLHttpRequest();

    if (chatId === ""){
        alert("Provide a chat_id to save a file !")
    }else{
        document.getElementById("response").innerHTML = "Sending the file..."
        formData.append("chat_id", chatId);
        // HTML file input, chosen by user
        formData.append("file", fileElement.files[0]);
        request.open("POST", "/api/upload");
        request.onload  = function() {
            const responseHtml = `
                    <b>- File_name :</b> <i style="color: #0069ff;">${JSON.parse(request.response)["json_map"]["file"]["file_name"]}</i> </li>
                    <br/><b>- File_key :</b> <i style="color: red;">${JSON.parse(request.response)["file_key"]}</i> </li>
                    <br/><b>- Chunks :</b> ${JSON.parse(request.response)["json_map"]["cloud_map"].length} </li>
                    <br/><b>- Timestamp :</b> ${new Date().toUTCString()} </li><br/>`;
            
            if (JSON.parse(request.response)["json_map"]["cloud_map"].length === 0){
                document.getElementById("response").innerHTML = "Something went wrong, please check your chat-id";
            }else{
                document.getElementById("response").innerHTML = responseHtml;
            }
            // do something with jsonResponse
         };
        request.send(formData);
    }
}