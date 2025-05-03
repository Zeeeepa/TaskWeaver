// TaskWeaver UI JavaScript

// DOM Elements
const credentialsForm = document.getElementById('credentials-form');
const repoSelectionContainer = document.getElementById('repo-selection-container');
const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const statusContainer = document.getElementById('status-container');

// Current state
let selectedRepo = '';

// Event Listeners
credentialsForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(credentialsForm);
    
    try {
        updateStatus('Setting API credentials...');
        
        const response = await fetch('/api/credentials', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            updateStatus('API credentials set successfully.');
            
            // Load repositories
            if (data.repos && data.repos.length > 0) {
                loadRepositories(data.repos);
            } else {
                repoSelectionContainer.innerHTML = '<p>No repositories found. Please check your GitHub token.</p>';
            }
        } else {
            updateStatus(`Error: ${data.message}`, true);
        }
    } catch (error) {
        updateStatus(`Error: ${error.message}`, true);
    }
});

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    chatInput.value = '';
    
    try {
        updateStatus('Processing your message...');
        
        const formData = new FormData();
        formData.append('message', message);
        
        const response = await fetch('/api/converse', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            // Add system response to chat
            addMessage('Message processed. Requirements documentation updated.', 'system');
            
            updateStatus('Ready for your next message.');
        } else {
            addMessage(`Error: ${data.message}`, 'system');
            updateStatus(`Error: ${data.message}`, true);
        }
    } catch (error) {
        addMessage(`Error: ${error.message}`, 'system');
        updateStatus(`Error: ${error.message}`, true);
    }
});

// Helper Functions
function loadRepositories(repos) {
    let html = '<div class="mb-3">';
    html += '<label for="repo-select" class="form-label">Select Repository</label>';
    html += '<select class="form-select" id="repo-select">';
    html += '<option value="">-- Select a repository --</option>';
    
    repos.forEach(repo => {
        html += `<option value="${repo}">${repo}</option>`;
    });
    
    html += '</select>';
    html += '</div>';
    html += '<button id="select-repo-btn" class="btn btn-primary">Select Repository</button>';
    
    repoSelectionContainer.innerHTML = html;
    
    // Add event listener to the select repository button
    document.getElementById('select-repo-btn').addEventListener('click', async () => {
        const repoSelect = document.getElementById('repo-select');
        const repo = repoSelect.value;
        
        if (!repo) {
            updateStatus('Please select a repository.', true);
            return;
        }
        
        try {
            updateStatus(`Selecting repository: ${repo}...`);
            
            const formData = new FormData();
            formData.append('repo_name', repo);
            
            const response = await fetch('/api/select-repo', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                selectedRepo = repo;
                updateStatus(`Repository selected: ${repo}`);
                addMessage(`Repository selected: ${repo}`, 'system');
            } else {
                updateStatus(`Error: ${data.message}`, true);
            }
        } catch (error) {
            updateStatus(`Error: ${error.message}`, true);
        }
    });
}

function addMessage(message, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add(type === 'user' ? 'user-message' : 'system-message');
    messageElement.textContent = message;
    
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function updateStatus(message, isError = false) {
    const statusElement = document.createElement('p');
    statusElement.textContent = message;
    
    if (isError) {
        statusElement.classList.add('text-danger');
    }
    
    statusContainer.innerHTML = '';
    statusContainer.appendChild(statusElement);
}

// Check Codegen status on page load
async function checkCodegenStatus() {
    try {
        const response = await fetch('/api/codegen/status');
        const data = await response.json();
        
        if (data.initialized) {
            updateStatus('Codegen integration is initialized.');
            
            // Get repositories
            const reposResponse = await fetch('/api/codegen/repositories');
            const reposData = await reposResponse.json();
            
            if (reposData.success && reposData.repositories.length > 0) {
                loadRepositories(reposData.repositories);
                
                if (reposData.active_repository) {
                    selectedRepo = reposData.active_repository;
                    updateStatus(`Active repository: ${selectedRepo}`);
                }
            }
        }
    } catch (error) {
        console.error('Error checking Codegen status:', error);
    }
}

// Initialize the page
window.addEventListener('DOMContentLoaded', () => {
    checkCodegenStatus();
});

