// TaskWeaver UI JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // OpenAI Settings Form
    const openaiSettingsForm = document.getElementById('openai-settings-form');
    if (openaiSettingsForm) {
        openaiSettingsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(openaiSettingsForm);
            
            // Send the form data to the server
            fetch('/api/openai-settings', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Show success message
                    const statusContainer = document.getElementById('status-container');
                    if (statusContainer) {
                        statusContainer.innerHTML = `<div class="alert alert-success">OpenAI settings updated successfully!</div>`;
                    }
                } else {
                    // Show error message
                    const statusContainer = document.getElementById('status-container');
                    if (statusContainer) {
                        statusContainer.innerHTML = `<div class="alert alert-danger">Error updating OpenAI settings: ${data.message}</div>`;
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Show error message
                const statusContainer = document.getElementById('status-container');
                if (statusContainer) {
                    statusContainer.innerHTML = `<div class="alert alert-danger">Error updating OpenAI settings: ${error.message}</div>`;
                }
            });
        });
    }
    
    // API Credentials Form
    const credentialsForm = document.getElementById('credentials-form');
    if (credentialsForm) {
        credentialsForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(credentialsForm);
            
            // Send the form data to the server
            fetch('/api/credentials', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Show success message
                    const statusContainer = document.getElementById('status-container');
                    if (statusContainer) {
                        statusContainer.innerHTML = `<div class="alert alert-success">API credentials updated successfully!</div>`;
                    }
                    
                    // Update repository selection
                    updateRepositorySelection(data.repos);
                } else {
                    // Show error message
                    const statusContainer = document.getElementById('status-container');
                    if (statusContainer) {
                        statusContainer.innerHTML = `<div class="alert alert-danger">Error updating API credentials: ${data.message}</div>`;
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Show error message
                const statusContainer = document.getElementById('status-container');
                if (statusContainer) {
                    statusContainer.innerHTML = `<div class="alert alert-danger">Error updating API credentials: ${error.message}</div>`;
                }
            });
        });
    }
    
    // Chat Form
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const chatInput = document.getElementById('chat-input');
            const message = chatInput.value.trim();
            
            if (message) {
                // Add user message to chat
                const chatContainer = document.getElementById('chat-container');
                if (chatContainer) {
                    chatContainer.innerHTML += `<div class="user-message">${message}</div>`;
                }
                
                // Clear input
                chatInput.value = '';
                
                // Send message to server
                const formData = new FormData();
                formData.append('message', message);
                
                fetch('/api/converse', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Add system message to chat
                        if (chatContainer) {
                            chatContainer.innerHTML += `<div class="system-message">${data.requirements}</div>`;
                            
                            // Scroll to bottom
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }
                    } else {
                        // Show error message
                        if (chatContainer) {
                            chatContainer.innerHTML += `<div class="system-message error">Error: ${data.message}</div>`;
                            
                            // Scroll to bottom
                            chatContainer.scrollTop = chatContainer.scrollHeight;
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Show error message
                    if (chatContainer) {
                        chatContainer.innerHTML += `<div class="system-message error">Error: ${error.message}</div>`;
                        
                        // Scroll to bottom
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                    }
                });
            }
        });
    }
    
    // Function to update repository selection
    function updateRepositorySelection(repos) {
        const repoSelectionContainer = document.getElementById('repo-selection-container');
        if (repoSelectionContainer) {
            if (repos && repos.length > 0) {
                let html = '<form id="repo-form">';
                html += '<div class="mb-3">';
                html += '<label for="repo-select" class="form-label">Select Repository</label>';
                html += '<select class="form-select" id="repo-select" name="repo_name">';
                
                repos.forEach(repo => {
                    html += `<option value="${repo}">${repo}</option>`;
                });
                
                html += '</select>';
                html += '</div>';
                html += '<button type="submit" class="btn btn-primary">Set Repository</button>';
                html += '</form>';
                
                repoSelectionContainer.innerHTML = html;
                
                // Add event listener to the form
                const repoForm = document.getElementById('repo-form');
                if (repoForm) {
                    repoForm.addEventListener('submit', function(e) {
                        e.preventDefault();
                        
                        const formData = new FormData(repoForm);
                        
                        // Send the form data to the server
                        fetch('/api/select-repo', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'success') {
                                // Show success message
                                const statusContainer = document.getElementById('status-container');
                                if (statusContainer) {
                                    statusContainer.innerHTML = `<div class="alert alert-success">Repository selected successfully!</div>`;
                                }
                            } else {
                                // Show error message
                                const statusContainer = document.getElementById('status-container');
                                if (statusContainer) {
                                    statusContainer.innerHTML = `<div class="alert alert-danger">Error selecting repository: ${data.message}</div>`;
                                }
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            // Show error message
                            const statusContainer = document.getElementById('status-container');
                            if (statusContainer) {
                                statusContainer.innerHTML = `<div class="alert alert-danger">Error selecting repository: ${error.message}</div>`;
                            }
                        });
                    });
                }
            } else {
                repoSelectionContainer.innerHTML = '<p>No repositories available. Please check your API credentials.</p>';
            }
        }
    }
});

