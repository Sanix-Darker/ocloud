const request = new XMLHttpRequest();
let savedModalContent = null;
let datas = null;
let chatId = null;

const init = () => {
	var router = new Router([
		new Route("home", "./home.html", true),
		new Route("app", "./app.html"),
	])
}
init()


const ObjectLength = (object) => {
	var length = 0
	for (var key in object) {
		if (object.hasOwnProperty(key)) {
			++length
		}
	}
	return length
}

const copy = () => {
	var fileKey = document.getElementById("fileKey")
	fileKey.select()
	fileKey.setSelectionRange(0, 99999)
	document.execCommand("copy")

	console.log("Copied the text: " + fileKey.value)
}

const showSavedModal = (data = null) => {
    if (data !== null){
        savedModalContent = new BSN.Modal("#res", {
            content: `<div class="modal-body">
            <p class="alert alert-success">
            🎉 ${data.message}<p/>
            <p>
                <b>File name :</b> 
                <span class="text-primary">
                    ${data.json_map.file.file_name}
                    </span>
            </p>
            <label for="fileKey"><b>File key : </b></label>
            <div class="input-group input-group-sm mb-3">
                <input type="text" class="form-control"
                value="${data.file_key}" id="fileKey">
                <div class="input-group-append">
                <button type="button" class="btn btn-secondary" onclick="copy()">Copy</button>
                </div>
            </div>
            <p>
                <b>Download-link :</b> 
                <a target="_blank" class="h6 small" href="${location.origin + "/api/file/" + data.file_key}">
                    ${data.file_key}
                </a>
            </p>
            <section>
                <b>Chunks :</b> ${data.json_map.cloud_map.length}
            </section>
            <section><b>Timestamp :</b> ${new Date().toUTCString()}</section>
            <p class="alert alert-warning">Make sure to save that <b>File key</b>, because it's the only key that will allow you to regenerate your file !<p/>
                    </div>`,
            backdrop: true,
            keyboard: true,
        });
    }
    savedModalContent.show()
}

const uploadFile = (event) => {
	event.preventDefault()
    event.target.setAttribute("disabled", "true")

    datas = new FormData()
    chatId = document.getElementById("chat_id").value
    const fileElement = document.getElementById("file_id")

    if (chatId === "" && chatId.length <= 5) {
        alert("Provide a valid chat_id to save a file !")
        event.target.removeAttribute("disabled")
    } else {
        if (fileElement.files.length === 0) {
            alert("Provide a file please !")
            event.target.removeAttribute("disabled")
        } else {
            document.getElementById("response").style.display = "block"
            document.getElementById("response").innerHTML = "Sending the file..."
            document.getElementById("file_key_output").innerHTML = ""
            // user datas
            datas.append("chat_id", chatId)
            datas.append("file", fileElement.files[0])

            localStorage.setItem("chatId", chatId);

            fetch(
                "/api/upload",{
                    method: "post",
                    body: datas,
                })
                .then((response) => {
                    return response.json()
                })
                .then((data) => {
                    if (data.status === 403) {
                        alert("[+] Your file is too Large !")
                    } else if (data.status === "success") {
                        showSavedModal(data);
                        event.target.removeAttribute("disabled")
                        document.getElementById("file_key_output").innerHTML = "File-key: " + data.file_key
                        document.getElementById("response").style.display = "none"
                    } else if (data.status === "error") {
                        document.getElementById(
                            "response"
                        ).innerHTML = `<p class="alert alert-danger">Something went wrong, please check your chat-id and your file</p>`
                    } else {
                        if (data.json_map.file_map.length <= 0) {
                            document.getElementById(
                                "response"
                            ).innerHTML = `<p class="alert alert-danger">Something went wrong, please check your chat-id and your file</p>`
                        } else {
                            document.getElementById("response").innerHTML = responseHtml
                        }
                    }
                })
                .catch(function (error) {
                    console.log("Request failed - ", error)
                    event.target.removeAttribute("disabled")
                });
        }
    }
}

const generateDownloadLink = () => {
	const fileKey = document.getElementById("file_key").value;
	if (fileKey === "" && fileKey.length <= 20) {
		alert("Provide a file_key to get a download file link !")
	} else {
		document.getElementById("response2").innerHTML = "Generating the file..."
		fetch(
			`/api/download/${fileKey}`
		)
			.then((response) => {
				return response.json()
			})
			.then((data) => {
				if (data.status === "success") {
					document.getElementById("response2").innerHTML = `
                        <a href='${data.download_link}' class="btn btn-success btn-block" target='_blank'>⇣ Download your file</a>
                        <p class="alert alert-warning">All files are deleted 24 hours after the download link is generated, but you can generate them anytime using the file-key.</p>`
				} else if (JSON.parse(request.response)["status"] === "error") {
					document.getElementById(
						"response2"
					).innerHTML = `<p class="alert alert-danger">Something went wrong, please check your file-key/i>`
				} else {
					if (
						typeof JSON.parse(request.response)["download_link"] === "undefined"
					) {
						document.getElementById(
							"response2"
						).innerHTML = `<p class="alert alert-danger">Something went wrong, please check your file-key.</p>`
					} else {
						document.getElementById("response2").innerHTML = responseHtml
					}
				}
			});
	}
}

// let fetch the numbr of files
const refreshCount = () => {
    request.open("GET", "/api/count");
    request.onload  = function() {
        console.log("[+] res: ", request.response);
        document.getElementById("count").innerHTML = JSON.parse(request.response)["count"] + " files saved.";
    }
    request.send(null);
};



const main = () => {
    setTimeout(() => {
        const params = new URLSearchParams(window.location.search)
        if (typeof params.get('chat_id') !== "undefined" && params.get('chat_id') !== null){
            localStorage.setItem("chatId", params.get('chat_id'));
            document.getElementById("chat_id").value = params.get('chat_id');
        }
        // We try to set the precedent OgramCloud chat-id
        document.getElementById("chat_id").value = localStorage.getItem("chatId");
        refreshCount();

        document.getElementById("file_id").onchange = () => {
            const fileName = document.getElementById("file_id").value.split("\\").pop();
            const fileLabel = document.querySelector(".custom-file-label");
            fileLabel.classList.add("selected")
            fileLabel.innerHTML = fileName;
        };

    }, 1500);
}

main();
