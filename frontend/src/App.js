import React, { useState, useEffect, useCallback } from 'react';
import { jobService } from './services/api';
import UrlForm from './components/UrlForm';
import ProgressView from './components/ProgressView';
import ResultsView from './components/ResultsView';
import Alert from './components/Alert';

const App = () => {
  const [currentJob, setCurrentJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);
  const [pollingInterval, setPollingInterval] = useState(null);
  const [appState, setAppState] = useState('idle'); // 'idle', 'processing', 'completed', 'error'
  const [formKey, setFormKey] = useState(Date.now()); // Unique key for form reset

  // Load job progress from API
  const loadJobProgress = useCallback(async (jobId) => {
    try {
      const progressData = await jobService.getJobProgress(jobId);
      setCurrentJob(prev => ({ ...prev, ...progressData }));
      
      // Update app state based on job status
      if (progressData.status === 'completed') {
        setAppState('completed');
        stopPolling();
        // Load full job data to get llm_text_content
        const fullJob = await jobService.getJob(jobId);
        setCurrentJob(fullJob);
      } else if (progressData.status === 'error') {
        setAppState('error');
        stopPolling();
      }
    } catch (error) {
      console.error('Error loading job progress:', error);
      showAlert('Failed to load job progress. Please try again.', 'danger');
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
    setCurrentJob(job);
    
    // If job already exists and is completed, go directly to results
    if (job.is_existing && job.status === 'completed') {
      setAppState('completed');
      showAlert(
        `Job ${job.id} already exists and is completed! ${job.message}`,
        'info'
      );
      // Load full job data to get llm_text_content
      loadFullJobData(job.id);
    } else if (job.is_existing && job.status === 'error') {
      setAppState('error');
      showAlert(
        `Job ${job.id} already exists but failed. ${job.message}`,
        'warning'
      );
    } else {
      // New job or existing job still processing
      setAppState('processing');
      showAlert(
        `Job ${job.id} ${job.is_existing ? 'retrieved' : 'created'} successfully! ${job.message}`,
        'success'
      );
      startPolling(job.id);
    }
  };

  // Load full job data for completed jobs
  const loadFullJobData = async (jobId) => {
    try {
      const fullJob = await jobService.getJob(jobId);
      setCurrentJob(fullJob);
    } catch (error) {
      console.error('Error loading full job data:', error);
      showAlert('Failed to load job details. Please try again.', 'danger');
    }
  };

  // Handle new submission
  const handleNewSubmission = () => {
    console.log('Resetting app state for new submission');
    stopPolling(); // Stop any ongoing polling
    setPollingInterval(null); // Clear polling interval state
    setCurrentJob(null);
    setAppState('idle');
    setAlert(null);
    setLoading(false); // Reset loading state
    setFormKey(Date.now()); // Force form re-render
  };

  // Start polling for job progress
  const startPolling = (jobId) => {
    if (pollingInterval) return;
    
    const interval = setInterval(() => {
      loadJobProgress(jobId);
    }, 2000); // Poll every 2 seconds
    
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
    console.log('App mounted, current state:', { appState, currentJob: currentJob?.id });
    // Cleanup on unmount
    return () => {
      stopPolling();
    };
  }, []);

  // Debug app state changes
  useEffect(() => {
    console.log('App state changed:', { appState, currentJob: currentJob?.id, status: currentJob?.status });
  }, [appState, currentJob]);

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

        {/* Main Content */}
        <div className="row">
          <div className="col-12">
            {appState === 'idle' && (
              <UrlForm
                key={formKey}
                onJobCreated={handleJobCreated}
                onError={showAlert}
              />
            )}
            
            {appState === 'processing' && currentJob && (
              <ProgressView
                progress={currentJob.progress_percentage}
                message={currentJob.progress_message}
                status={currentJob.status}
              />
            )}
            
            {appState === 'completed' && currentJob && (
              <ResultsView
                job={currentJob}
                onNewSubmission={handleNewSubmission}
              />
            )}
            
            {appState === 'error' && currentJob && (
              <div className="card">
                <div className="card-header">
                  <h5 className="mb-0 text-danger">
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    Processing Failed
                  </h5>
                </div>
                <div className="card-body">
                  <p className="text-muted">An error occurred while processing your request.</p>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleNewSubmission}
                  >
                    <i className="fas fa-plus me-2"></i>
                    Try Again
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;



