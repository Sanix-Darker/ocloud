/**
 * The MAIN script
 */

const main = () => {
    init()
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
    }, 1700);
}

main();
