// TaskWeaver with Codegen UI Scripts

$(document).ready(function() {
    // Check integration status on page load
    checkIntegrationStatus();
    
    // Credentials form submission
    $('#credentials-form').submit(function(e) {
        e.preventDefault();
        
        const githubToken = $('#github-token').val();
        const codegenToken = $('#codegen-token').val();
        const ngrokToken = $('#ngrok-token').val();
        const codegenOrgId = $('#codegen-org-id').val();
        
        if (!githubToken || !codegenToken || !ngrokToken || !codegenOrgId) {
            alert('Please fill in all credential fields.');
            return;
        }
        
        // Set connection status to connecting
        $('#connection-status').removeClass('bg-secondary bg-success').addClass('bg-warning').text('Connecting...');
        
        // Send credentials to server
        $.ajax({
            url: '/api/set_credentials',
            method: 'POST',
            data: {
                github_token: githubToken,
                codegen_token: codegenToken,
                ngrok_token: ngrokToken,
                codegen_org_id: codegenOrgId
            },
            success: function(response) {
                if (response.success) {
                    $('#connection-status').removeClass('bg-warning').addClass('bg-success').text('Connected');
                    
                    // Get repositories
                    getRepositories();
                    
                    // Check integration status
                    checkIntegrationStatus();
                } else {
                    $('#connection-status').removeClass('bg-warning').addClass('bg-danger').text('Connection Failed');
                    alert('Failed to connect with the provided credentials.');
                }
            },
            error: function() {
                $('#connection-status').removeClass('bg-warning').addClass('bg-danger').text('Connection Failed');
                alert('An error occurred while connecting.');
            }
        });
    });
    
    // Get repositories
    function getRepositories() {
        $.ajax({
            url: '/api/get_repos',
            method: 'GET',
            success: function(response) {
                const repos = response.repos;
                
                if (repos && repos.length > 0) {
                    // Enable repository select
                    $('#repo-select').prop('disabled', false);
                    $('#set-repo-btn').prop('disabled', false);
                    
                    // Clear existing options
                    $('#repo-select').empty();
                    $('#codegen-repo').empty();
                    
                    // Add default option
                    $('#repo-select').append('<option selected>Select a repository</option>');
                    $('#codegen-repo').append('<option value="" selected>Use active repository</option>');
                    
                    // Add repositories
                    repos.forEach(function(repo) {
                        $('#repo-select').append(`<option value="${repo.name}" data-description="${repo.description}" data-language="${repo.language}" data-stars="${repo.stars}" data-forks="${repo.forks}">${repo.name}</option>`);
                        $('#codegen-repo').append(`<option value="${repo.name}">${repo.name}</option>`);
                    });
                } else {
                    alert('No repositories found.');
                }
            },
            error: function() {
                alert('An error occurred while getting repositories.');
            }
        });
    }
    
    // Set repository
    $('#set-repo-btn').click(function() {
        const repoName = $('#repo-select').val();
        
        if (repoName === 'Select a repository') {
            alert('Please select a repository.');
            return;
        }
        
        $.ajax({
            url: '/api/set_repository',
            method: 'POST',
            data: {
                repo_name: repoName
            },
            success: function(response) {
                if (response.success) {
                    alert(`Repository ${repoName} set successfully.`);
                    checkIntegrationStatus();
                } else {
                    alert('Failed to set repository.');
                }
            },
            error: function() {
                alert('An error occurred while setting repository.');
            }
        });
    });
    
    // Show repository details when selected
    $('#repo-select').change(function() {
        const repoName = $(this).val();
        
        if (repoName === 'Select a repository') {
            $('#repo-details').addClass('d-none');
            return;
        }
        
        const option = $(this).find('option:selected');
        const description = option.data('description');
        const language = option.data('language');
        const stars = option.data('stars');
        const forks = option.data('forks');
        
        $('#repo-description').text(description);
        $('#repo-language').text(language);
        $('#repo-stars').text(stars);
        $('#repo-forks').text(forks);
        
        $('#repo-details').removeClass('d-none');
    });
    
    // Check integration status
    function checkIntegrationStatus() {
        $.ajax({
            url: '/api/get_integration_status',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    const status = response.status;
                    
                    // Update status badges
                    $('#github-status').removeClass('bg-secondary').addClass(status.github_connected ? 'bg-success' : 'bg-danger').text(status.github_connected ? 'Connected' : 'Disconnected');
                    $('#codegen-status').removeClass('bg-secondary').addClass(status.codegen_connected ? 'bg-success' : 'bg-danger').text(status.codegen_connected ? 'Connected' : 'Disconnected');
                    $('#ngrok-status').removeClass('bg-secondary').addClass(status.ngrok_connected ? 'bg-success' : 'bg-danger').text(status.ngrok_connected ? 'Connected' : 'Disconnected');
                    $('#workflow-status').removeClass('bg-secondary').addClass(status.workflow_manager ? 'bg-success' : 'bg-danger').text(status.workflow_manager ? 'Active' : 'Inactive');
                    
                    // Update repository status
                    if (status.repository) {
                        $('#repo-status').removeClass('bg-secondary').addClass('bg-success').text(status.repository);
                    } else {
                        $('#repo-status').removeClass('bg-success').addClass('bg-secondary').text('None');
                    }
                    
                    // Update connection status
                    if (status.initialized) {
                        $('#connection-status').removeClass('bg-secondary bg-warning').addClass('bg-success').text('Connected');
                    } else {
                        $('#connection-status').removeClass('bg-success bg-warning').addClass('bg-secondary').text('Not Connected');
                    }
                }
            }
        });
    }
    
    // Save requirements to repository
    $('#save-requirements-btn').click(function() {
        const requirements = $('#requirements-container').val();
        
        if (!requirements) {
            alert('Please enter requirements.');
            return;
        }
        
        $.ajax({
            url: '/api/create_requirements',
            method: 'POST',
            data: {
                requirements: requirements
            },
            success: function(response) {
                if (response.success) {
                    alert('Requirements saved to repository successfully.');
                } else {
                    alert('Failed to save requirements: ' + (response.error || 'Unknown error'));
                }
            },
            error: function() {
                alert('An error occurred while saving requirements.');
            }
        });
    });
    
    // Start workflow
    $('#start-workflow-btn').click(function() {
        $.ajax({
            url: '/api/start_workflow',
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    alert('Workflow started successfully.');
                    checkIntegrationStatus();
                } else {
                    alert('Failed to start workflow.');
                }
            },
            error: function() {
                alert('An error occurred while starting workflow.');
            }
        });
    });
    
    // Stop workflow
    $('#stop-workflow-btn').click(function() {
        $.ajax({
            url: '/api/stop_workflow',
            method: 'POST',
            success: function(response) {
                if (response.success) {
                    alert('Workflow stopped successfully.');
                    checkIntegrationStatus();
                } else {
                    alert('Failed to stop workflow.');
                }
            },
            error: function() {
                alert('An error occurred while stopping workflow.');
            }
        });
    });
    
    // Send to Codegen
    $('#send-to-codegen-btn').click(function() {
        const prompt = $('#codegen-prompt').val();
        const repoName = $('#codegen-repo').val();
        
        if (!prompt) {
            alert('Please enter a prompt for Codegen.');
            return;
        }
        
        $.ajax({
            url: '/api/create_task',
            method: 'POST',
            data: {
                prompt: prompt,
                repo_name: repoName
            },
            success: function(response) {
                if (response.success) {
                    alert(`Task created successfully with ID: ${response.task_id}`);
                    // Switch to tasks tab
                    $('#tasks-tab').tab('show');
                    // Refresh tasks
                    refreshTasks();
                } else {
                    alert('Failed to create task: ' + (response.error || 'Unknown error'));
                }
            },
            error: function() {
                alert('An error occurred while creating task.');
            }
        });
    });
    
    // Refresh tasks
    function refreshTasks() {
        $.ajax({
            url: '/api/get_active_tasks',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    const tasks = response.tasks;
                    
                    // Clear tasks container
                    $('#tasks-container').empty();
                    
                    if (Object.keys(tasks).length === 0) {
                        $('#tasks-container').html('<p class="text-muted">No active tasks.</p>');
                        return;
                    }
                    
                    // Add tasks
                    for (const taskId in tasks) {
                        const task = tasks[taskId];
                        let statusClass = 'task-item';
                        let statusBadge = '<span class="badge bg-secondary">Unknown</span>';
                        
                        if (task.completed) {
                            statusClass += ' task-completed';
                            statusBadge = '<span class="badge bg-success">Completed</span>';
                        } else if (task.status === 'failed') {
                            statusClass += ' task-failed';
                            statusBadge = '<span class="badge bg-danger">Failed</span>';
                        } else if (task.status === 'running') {
                            statusClass += ' task-running';
                            statusBadge = '<span class="badge bg-warning">Running</span>';
                        }
                        
                        const taskHtml = `
                            <div class="${statusClass}">
                                <div class="d-flex justify-content-between align-items-center">
                                    <h6 class="mb-1">Task ID: ${task.id}</h6>
                                    ${statusBadge}
                                </div>
                                <p class="mb-1"><strong>Repository:</strong> ${task.repo_name || 'Default'}</p>
                                <p class="mb-1"><strong>Prompt:</strong> ${task.prompt}</p>
                                <p class="mb-1"><strong>Created:</strong> ${task.created_at || 'Unknown'}</p>
                                <p class="mb-1"><strong>Updated:</strong> ${task.updated_at || 'Unknown'}</p>
                                ${task.result ? `<p class="mb-1"><strong>Result:</strong> ${task.result}</p>` : ''}
                                <button class="btn btn-sm btn-info refresh-task-btn" data-task-id="${task.id}">Refresh Status</button>
                            </div>
                        `;
                        
                        $('#tasks-container').append(taskHtml);
                    }
                    
                    // Add refresh task button handler
                    $('.refresh-task-btn').click(function() {
                        const taskId = $(this).data('task-id');
                        refreshTaskStatus(taskId);
                    });
                }
            }
        });
    }
    
    // Refresh task status
    function refreshTaskStatus(taskId) {
        $.ajax({
            url: `/api/get_task_status/${taskId}`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    refreshTasks();
                } else {
                    alert('Failed to refresh task status: ' + (response.error || 'Unknown error'));
                }
            },
            error: function() {
                alert('An error occurred while refreshing task status.');
            }
        });
    }
    
    // Refresh tasks button
    $('#refresh-tasks-btn').click(function() {
        refreshTasks();
    });
    
    // Chat functionality
    $('#send-btn').click(function() {
        const message = $('#chat-input').val();
        
        if (!message) {
            return;
        }
        
        // Add user message to chat
        $('#chat-container').append(`
            <div class="message user-message">
                <strong>You:</strong> ${message}
            </div>
        `);
        
        // Clear input
        $('#chat-input').val('');
        
        // Scroll to bottom
        $('#chat-container').scrollTop($('#chat-container')[0].scrollHeight);
        
        // TODO: Implement chat functionality with TaskWeaver
        // For now, just add a placeholder response
        setTimeout(function() {
            $('#chat-container').append(`
                <div class="message system-message">
                    <strong>TaskWeaver:</strong> I'm processing your request: "${message}"
                </div>
            `);
            
            // Scroll to bottom
            $('#chat-container').scrollTop($('#chat-container')[0].scrollHeight);
            
            // Generate requirements based on conversation
            if ($('#requirements-container').val() === '') {
                const requirements = `# Requirements Document\n\n## Feature Request\n\n${message}\n\n## Implementation Plan\n\n1. Analyze the requirements\n2. Design the solution\n3. Implement the solution\n4. Test the implementation\n5. Deploy the solution`;
                
                $('#requirements-container').val(requirements);
            }
        }, 1000);
    });
    
    // Enter key in chat input
    $('#chat-input').keypress(function(e) {
        if (e.which === 13) {
            $('#send-btn').click();
            return false;
        }
    });
    
    // Refresh tasks on tab show
    $('#tasks-tab').on('shown.bs.tab', function() {
        refreshTasks();
    });
    
    // Check integration status on tab show
    $('#setup-tab').on('shown.bs.tab', function() {
        checkIntegrationStatus();
    });
});

