import React, { useState, useEffect, useCallback } from 'react';
import { jobService } from './services/api';
import UrlForm from './components/UrlForm';
import JobsTable from './components/JobsTable';
import Alert from './components/Alert';

const App = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);

  // Load jobs from API
  const loadJobs = useCallback(async () => {
    setLoading(true);
    try {
      const jobsData = await jobService.getJobs();
      setJobs(jobsData);
    } catch (error) {
      console.error('Error loading jobs:', error);
      showAlert('Failed to load jobs. Please try again.', 'danger');
    } finally {
      setLoading(false);
    }
  }, []);

  // Show alert message
  const showAlert = (message, type = 'info') => {
    setAlert({ message, type });
  };

  // Hide alert
  const hideAlert = () => {
    setAlert(null);
  };

  // Handle job creation
  const handleJobCreated = (job) => {
    showAlert(
      `Job ${job.id} ${job.is_existing ? 'retrieved' : 'created'} successfully! ${job.message}`,
      'success'
    );
    loadJobs(); // Reload jobs to show the new one
  };

  // Handle job update
  const handleJobUpdate = (updatedJob) => {
    setJobs(prevJobs => 
      prevJobs.map(job => 
        job.id === updatedJob.id ? updatedJob : job
      )
    );
  };

  // Handle refresh button
  const handleRefresh = () => {
    loadJobs();
  };

  // Start polling for job updates
  const startPolling = () => {
    if (pollingInterval) return;
    
    const interval = setInterval(() => {
      loadJobs();
    }, 3000); // Poll every 3 seconds
    
    setPollingInterval(interval);
  };

  // Stop polling
  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
    }
  };

  // Initialize component
  useEffect(() => {
    loadJobs();
    startPolling();

    // Cleanup on unmount
    return () => {
      stopPolling();
    };
  }, [loadJobs]);

  // Handle visibility change (resume polling when page becomes visible)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        loadJobs();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [loadJobs]);

  return (
    <div className="container-fluid">
      {/* Header */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary mb-4">
        <div className="container">
          <a className="navbar-brand" href="#">
            <i className="fas fa-robot me-2"></i>
            LLM Text Generator
          </a>
        </div>
      </nav>

      <div className="container">
        {/* Alert */}
        {alert && (
          <Alert
            message={alert.message}
            type={alert.type}
            onClose={hideAlert}
          />
        )}

        {/* URL Submission Form */}
        <div className="row mb-4">
          <div className="col-12">
            <UrlForm
              onJobCreated={handleJobCreated}
              onError={showAlert}
            />
          </div>
        </div>

        {/* Jobs Dashboard */}
        <div className="row">
          <div className="col-12">
            <div className="card">
              <div className="card-header d-flex justify-content-between align-items-center">
                <h5 className="mb-0">
                  <i className="fas fa-tasks me-2"></i>
                  Crawling Jobs
                </h5>
                <button
                  className="btn btn-outline-secondary btn-sm"
                  onClick={handleRefresh}
                  disabled={loading}
                >
                  <i className="fas fa-sync-alt me-1"></i>
                  Refresh
                </button>
              </div>
              <div className="card-body">
                {/* Loading indicator */}
                {loading && (
                  <div className="text-center py-4">
                    <div className="spinner-border text-primary" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                    <p className="mt-2 text-muted">Loading jobs...</p>
                  </div>
                )}

                {/* Jobs table */}
                {!loading && (
                  <JobsTable
                    jobs={jobs}
                    onJobUpdate={handleJobUpdate}
                    onError={showAlert}
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;

