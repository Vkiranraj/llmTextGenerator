import React, { useState } from 'react';
import { jobService } from '../services/api';

const ResultsView = ({ job, onNewSubmission }) => {
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(job.llm_text_content);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const handleDownload = () => {
    const blob = new Blob([job.llm_text_content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `llms_${job.id}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  return (
    <div className="card">
      <div className="card-header">
        <h5 className="mb-0">
          <i className="fas fa-check-circle text-success me-2"></i>
          LLM Text Generated Successfully
        </h5>
      </div>
      <div className="card-body">
        {/* Job Info */}
        <div className="row mb-4">
          <div className="col-md-6">
            <h6>URL Processed:</h6>
            <p className="text-muted">
              <a href={job.url} target="_blank" rel="noopener noreferrer">
                {job.url}
              </a>
            </p>
          </div>
          <div className="col-md-6">
            <h6>Status:</h6>
            <span className="badge bg-success">Completed</span>
            {job.email && (
              <div className="mt-2">
                <small className="text-muted">
                  <i className="fas fa-envelope me-1"></i>
                  Monitoring enabled for {job.email}
                </small>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="row mb-4">
          <div className="col-12">
            <div className="btn-group" role="group">
              <button
                type="button"
                className="btn btn-outline-primary"
                onClick={handleCopyToClipboard}
              >
                <i className="fas fa-copy me-2"></i>
                {copySuccess ? 'Copied!' : 'Copy to Clipboard'}
              </button>
              <button
                type="button"
                className="btn btn-outline-secondary"
                onClick={handleDownload}
              >
                <i className="fas fa-download me-2"></i>
                Download as .txt
              </button>
            </div>
          </div>
        </div>

        {/* LLM Text Content */}
        <div className="row">
          <div className="col-12">
            <h6>Generated LLM Text:</h6>
            <div className="border rounded p-3" style={{ maxHeight: '400px', overflowY: 'auto' }}>
              <pre 
                style={{ 
                  whiteSpace: 'pre-wrap', 
                  wordWrap: 'break-word',
                  margin: 0,
                  fontFamily: 'monospace',
                  fontSize: '0.9em'
                }}
              >
                {job.llm_text_content}
              </pre>
            </div>
          </div>
        </div>

        {/* New Submission Button */}
        <div className="row mt-4">
          <div className="col-12 text-center">
            <button
              type="button"
              className="btn btn-primary"
              onClick={onNewSubmission}
            >
              <i className="fas fa-plus me-2"></i>
              Process Another URL
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultsView;
