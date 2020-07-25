/**
 * The FUNCTIONS script
 */

 // Some global variables
let savedModalContent = null;
let datas = null;
let chatId = null;

const init = () => {
	var router = new Router([
        new Route("home", "./home.html", true),
		new Route("app", "./app.html"),
	])
}

const ObjectLength = (object) => {
	var length = 0
	for (var key in object) {
		if (object.hasOwnProperty(key)) {
			++length
		}
	}
	return length
}

/**
 * 
 */
const copy = () => {
	var fileKey = document.getElementById("fileKey")
	fileKey.select()
	fileKey.setSelectionRange(0, 99999)
	document.execCommand("copy");
}

/**
 * 
 * @param {*} data 
 */
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

/**
 * 
 * @param {*} event 
 */
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

            fetch("/api/upload",{
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
                        document.getElementById("file_key_output").innerHTML = "<kbd title='Click for details'>FileKey : " + data.file_key + "</kbd>" 
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
                .catch((error) => {
                    console.log("Request failed - ", error)
                    alert("An error occur, make sure to follow requirements !");
                    document.getElementById("response").style.display = "none"
                    event.target.removeAttribute("disabled")
                });
        }
    }
}

/**
 * 
 */
const generateDownloadLink = () => {
	const fileKey = document.getElementById("file_key").value;
	if (fileKey === "" && fileKey.length <= 20) {
		alert("Provide a file_key to get a download file link !")
	} else {
		document.getElementById("response2").innerHTML = "Generating the file..."
		fetch(`/api/download/${fileKey}`)
			.then((response) => {
				return response.json()
			})
			.then((data) => {
				if (data.status === "success") {
					document.getElementById("response2").innerHTML = `
                        <a href='${data.download_link}' class="btn btn-success btn-block" target='_blank'>⇣ Download your file</a>
                        <p class="alert alert-warning">All files are deleted 24 hours after the download link is generated, but you can generate them anytime using the file-key.</p>`
				} else if (data.status === "error") {
					document.getElementById(
						"response2"
					).innerHTML = `<p class="alert alert-danger">Something went wrong, please check your file-key/i>`
				} else {
					if (
						typeof data.download_link === "undefined"
					) {
						document.getElementById(
							"response2"
						).innerHTML = `<p class="alert alert-danger">Something went wrong, please check your file-key.</p>`
					} else {
						document.getElementById("response2").innerHTML = responseHtml
					}
				}
			}).catch((error) => {
                console.log("Request failed - ", error)
                alert("An error occur, make sure to follow requirements !");
            });
	}
}

// let fetch the numbr of files
const refreshCount = () => {
    fetch(`/api/count`)
    .then((response) => {
        return response.json()
    }).then(data => {
        console.log("[+] res: ", data);
        document.getElementById("count").innerHTML = nFormatter(data.count) + " files saved.";
    }).catch(err => {
        console.log(err);
    });
};

// A digit formatter
const nFormatter = (num, digits=1) => {
    var si = [
      { value: 1, symbol: "" },
      { value: 1E3, symbol: "k" },
      { value: 1E6, symbol: "M" },
      { value: 1E9, symbol: "G" },
      { value: 1E12, symbol: "T" },
      { value: 1E15, symbol: "P" },
      { value: 1E18, symbol: "E" }
    ];
    var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
    var i;
    for (i = si.length - 1; i > 0; i--) {
      if (num >= si[i].value) {
        break;
      }
    }
    return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
}