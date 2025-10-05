// LLM Text Generator - Frontend JavaScript
class CrawlerDashboard {
    constructor() {
        this.apiBase = 'http://localhost:8000'; // Backend API URL
        this.pollingInterval = 3000; // Poll every 3 seconds
        this.pollingTimer = null;
        this.jobs = new Map(); // Store jobs for efficient updates
        
        this.initializeEventListeners();
        this.loadJobs();
        this.startPolling();
    }

    initializeEventListeners() {
        // URL submission form
        document.getElementById('urlForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitUrl();
        });

        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadJobs();
        });

        // Auto-refresh when page becomes visible
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.loadJobs();
            }
        });
    }

    async submitUrl() {
        const urlInput = document.getElementById('urlInput');
        const submitBtn = document.getElementById('submitBtn');
        const url = urlInput.value.trim();

        if (!url) {
            this.showAlert('Please enter a valid URL', 'danger');
            return;
        }

        // Disable form during submission
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Submitting...';

        try {
            const response = await fetch(`${this.apiBase}/jobs/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url })
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to submit URL');
            }

            const job = await response.json();
            
            // Show success message
            this.showAlert(
                `Job ${job.id} ${job.is_existing ? 'retrieved' : 'created'} successfully! ${job.message}`, 
                'success'
            );

            // Clear form
            urlInput.value = '';
            
            // Reload jobs to show the new one
            this.loadJobs();

        } catch (error) {
            console.error('Error submitting URL:', error);
            this.showAlert(`Error: ${error.message}`, 'danger');
        } finally {
            // Re-enable form
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-play me-2"></i>Start Crawling';
        }
    }

    async loadJobs() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        const jobsContainer = document.getElementById('jobsContainer');
        
        loadingIndicator.style.display = 'block';
        jobsContainer.style.display = 'none';

        try {
            const response = await fetch(`${this.apiBase}/jobs/`);
            if (!response.ok) {
                throw new Error('Failed to load jobs');
            }

            const jobs = await response.json();
            this.displayJobs(jobs);

        } catch (error) {
            console.error('Error loading jobs:', error);
            this.showAlert('Failed to load jobs. Please try again.', 'danger');
        } finally {
            loadingIndicator.style.display = 'none';
            jobsContainer.style.display = 'block';
        }
    }

    displayJobs(jobs) {
        const jobsTable = document.getElementById('jobsTable');
        const noJobsMessage = document.getElementById('noJobsMessage');
        const jobsTableBody = document.getElementById('jobsTableBody');

        if (jobs.length === 0) {
            jobsTable.style.display = 'none';
            noJobsMessage.style.display = 'block';
            return;
        }

        jobsTable.style.display = 'block';
        noJobsMessage.style.display = 'none';

        // Clear existing rows
        jobsTableBody.innerHTML = '';

        // Sort jobs by creation date (newest first)
        jobs.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        jobs.forEach(job => {
            const row = this.createJobRow(job);
            jobsTableBody.appendChild(row);
            this.jobs.set(job.id, job);
        });
    }

    createJobRow(job) {
        const row = document.createElement('tr');
        row.id = `job-${job.id}`;

        const statusBadge = this.createStatusBadge(job.status);
        const downloadCell = this.createDownloadCell(job);
        const actionsCell = this.createActionsCell(job);

        row.innerHTML = `
            <td><strong>#${job.id}</strong></td>
            <td class="url-cell" title="${job.url}">${job.url}</td>
            <td>${statusBadge}</td>
            <td>${this.formatDate(job.created_at)}</td>
            <td>${job.last_crawled ? this.formatDate(job.last_crawled) : 'Never'}</td>
            <td>${downloadCell}</td>
            <td>${actionsCell}</td>
        `;

        return row;
    }

    createStatusBadge(status) {
        const statusConfig = {
            'pending': { class: 'status-pending', text: 'Pending', icon: 'fas fa-clock' },
            'in_progress': { class: 'status-in-progress', text: 'In Progress', icon: 'fas fa-spinner fa-spin' },
            'completed': { class: 'status-completed', text: 'Completed', icon: 'fas fa-check' },
            'error': { class: 'status-error', text: 'Error', icon: 'fas fa-exclamation-triangle' }
        };

        const config = statusConfig[status] || statusConfig['pending'];
        
        return `
            <span class="status-badge ${config.class}">
                <i class="${config.icon} me-1"></i>
                ${config.text}
            </span>
        `;
    }

    createDownloadCell(job) {
        if (job.status === 'completed' && job.llm_text_content) {
            return `
                <a href="${this.apiBase}/jobs/${job.id}/download" 
                   class="btn btn-success btn-sm download-btn" 
                   download="llm_${job.id}.txt">
                    <i class="fas fa-download me-1"></i>
                    Download
                </a>
            `;
        } else if (job.status === 'completed') {
                return '<span class="text-muted">No content</span>';
            }
        } else {
            return '<span class="text-muted">-</span>';
        }
    }

    createActionsCell(job) {
        let actions = '';

        if (job.status === 'error' && job.error_stack) {
            actions += `
                <button class="btn btn-outline-danger btn-sm error-btn me-2" 
                        onclick="dashboard.showError(${job.id})">
                    <i class="fas fa-bug me-1"></i>
                    View Error
                </button>
            `;
        }

        if (job.status === 'completed' || job.status === 'error') {
            actions += `
                <button class="btn btn-outline-secondary btn-sm" 
                        onclick="dashboard.refreshJob(${job.id})">
                    <i class="fas fa-sync me-1"></i>
                    Refresh
                </button>
            `;
        }

        return actions || '<span class="text-muted">-</span>';
    }

    showError(jobId) {
        const job = this.jobs.get(jobId);
        if (!job || !job.error_stack) return;

        document.getElementById('errorContent').textContent = job.error_stack;
        const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
        errorModal.show();
    }

    async refreshJob(jobId) {
        try {
            const response = await fetch(`${this.apiBase}/jobs/${jobId}`);
            if (!response.ok) {
                throw new Error('Failed to refresh job');
            }

            const job = await response.json();
            this.jobs.set(jobId, job);
            this.updateJobRow(jobId, job);

        } catch (error) {
            console.error('Error refreshing job:', error);
            this.showAlert('Failed to refresh job', 'danger');
        }
    }

    updateJobRow(jobId, job) {
        const row = document.getElementById(`job-${jobId}`);
        if (!row) return;

        // Update status
        const statusCell = row.cells[2];
        statusCell.innerHTML = this.createStatusBadge(job.status);

        // Update download cell
        const downloadCell = row.cells[5];
        downloadCell.innerHTML = this.createDownloadCell(job);

        // Update actions cell
        const actionsCell = row.cells[6];
        actionsCell.innerHTML = this.createActionsCell(job);

        // Update last crawled
        const lastCrawledCell = row.cells[4];
        lastCrawledCell.textContent = job.last_crawled ? this.formatDate(job.last_crawled) : 'Never';
    }

    startPolling() {
        // Poll every 3 seconds for job updates
        this.pollingTimer = setInterval(() => {
            this.loadJobs();
        }, this.pollingInterval);
    }

    stopPolling() {
        if (this.pollingTimer) {
            clearInterval(this.pollingTimer);
            this.pollingTimer = null;
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at top of container
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new CrawlerDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboard) {
        dashboard.stopPolling();
    }
});
