document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById("sidebar");
    const toggleBtn = document.getElementById("toggle-sidebar");
    const fileList = document.getElementById("file-list");
    const chatContainer = document.querySelector('.chat-container');

    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('open');
        if (sidebar.classList.contains('open')) {
            document.querySelector('.chat-container').style.marginLeft = '250px';
            document.querySelector('.bottom-section').style.marginLeft = '250px';
            document.querySelector('.header-banner').style.marginLeft = '250px';
        } else {
            document.querySelector('.chat-container').style.marginLeft = '50px';
            document.querySelector('.bottom-section').style.marginLeft = '0px';
            document.querySelector('.header-banner').style.marginLeft = '0px';
        }
    });

    function loadFiles() {
        fetch('http://localhost:5000/documents')
            .then(response => response.json())
            .then(files => {
                fileList.innerHTML = '';
                files.forEach(file => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        ${file}
                        <span class="delete-file" data-filename="${file}">&times;</span>
                    `;
                    fileList.appendChild(li);
                });
                addDeleteListeners();
            })
            .catch(error => console.log("Error loading files:", error));
    }

    loadFiles();

    function addDeleteListeners() {
        document.querySelectorAll('.delete-file').forEach(button => {
            button.addEventListener('click', function() {
                const fileName = this.getAttribute('data-filename');
                deleteFile(fileName);
            });
        });
    }

    function deleteFile(fileName) {
        fetch(`http://localhost:5000/delete/${fileName}`, {
            method: 'GET'
        })
            .then(response => {
                if (!response.ok) throw new Error('Delete failed');
                return response.text();
            })
            .then(() => {
                loadFiles(); // Reload file list after delete
            })
            .catch(error => console.error("Error deleting file:", error));
    }

    function toggleButtons(disable) {
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.disabled = disable;
            if (disable) {
                const spinner = document.createElement('span');
                spinner.className = 'spinner-border spinner-border-sm';
                spinner.setAttribute('role', 'status');
                spinner.setAttribute('aria-hidden', 'true');
                button.appendChild(spinner);
            } else {
                const spinner = button.querySelector('.spinner-border');
                if (spinner) spinner.remove();
            }
        });
    }

    function addMessage(content, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', type);
        messageElement.innerHTML = content;
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    document.getElementById('documents-btn').addEventListener("click", function() {
        window.location.href = "http://localhost:5000/documents";
    });

    document.getElementById('send-btn').addEventListener('click', function() {
        const askText = document.getElementById('ask-text').value.trim();
        if (!askText) {
            alert("Please enter text to search.");
            return;
        }

        addMessage(askText, 'sent');

        toggleButtons(true);

        fetch(`http://localhost:5000/question?question=${encodeURIComponent(askText)}`)
            .then(response => {
                if (!response.ok) throw new Error('Sent Input failed');
                return response.text();
            })
            .then(response => {
                addMessage(response, 'received');
            })
            .catch(() => {
                addMessage("An error occurred while processing your request.", 'received');
            })
            .finally(() => {
                toggleButtons(false);
                document.getElementById('ask-text').value = "";
            });
    });

    document.getElementById('upload-btn').addEventListener('click', function() {
        const fileInput = document.getElementById('pdf-file');
        if (fileInput.files.length === 0) {
            alert("Please select a PDF file to upload.");
            return;
        }

        const formData = new FormData();
        formData.append("document", fileInput.files[0]);

        toggleButtons(true);

        fetch('http://localhost:5000/upload', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) throw new Error('Upload failed');
                return response.text();
            })
            .then(() => {
                document.getElementById('upload-popup-body').textContent = "Document upload was successful!";
                document.getElementById('upload-popup').style.display = 'block';
                loadFiles();
            })
            .catch(() => {
                document.getElementById('upload-popup-body').textContent = "Document upload has failed!";
                document.getElementById('upload-popup').style.display = 'block';
            })
            .finally(() => {
                toggleButtons(false);
            });
    });

    document.getElementById('upload-popup-close').addEventListener('click', function() {
        document.getElementById('upload-popup').style.display = 'none';
    });
});
