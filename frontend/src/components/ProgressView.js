import React from 'react';

const ProgressView = ({ progress, message, status }) => {
  return (
    <div className="card">
      <div className="card-header">
        <h5 className="mb-0">
          <i className="fas fa-cog fa-spin me-2"></i>
          Processing Your Request
        </h5>
      </div>
      <div className="card-body">
        <div className="row">
          <div className="col-12">
            {/* Progress Bar */}
            <div className="mb-3">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <span className="text-muted">Progress</span>
                <span className="text-muted">{progress}%</span>
              </div>
              <div className="progress" style={{ height: '20px' }}>
                <div 
                  className="progress-bar progress-bar-striped progress-bar-animated bg-primary" 
                  role="progressbar" 
                  style={{ width: `${progress}%` }}
                  aria-valuenow={progress} 
                  aria-valuemin="0" 
                  aria-valuemax="100"
                >
                  {progress}%
                </div>
              </div>
            </div>

            {/* Current Step */}
            <div className="text-center">
              <div className="spinner-border text-primary mb-3" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
              <p className="text-muted mb-0">{message}</p>
              {status === 'error' && (
                <div className="alert alert-danger mt-3" role="alert">
                  <i className="fas fa-exclamation-triangle me-2"></i>
                  An error occurred during processing. Please try again.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressView;
