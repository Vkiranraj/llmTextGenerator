import React, { useState } from 'react';
import { jobService } from '../services/api';

const UrlForm = ({ onJobCreated, onError }) => {
  const [url, setUrl] = useState('');
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!url.trim()) {
      onError('Please enter a valid URL');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const job = await jobService.createJob(url.trim(), email.trim() || null);
      onJobCreated(job);
      setUrl('');
      setEmail('');
    } catch (error) {
      console.error('Error submitting URL:', error);
      onError(error.response?.data?.detail || error.message || 'Failed to submit URL');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h5 className="mb-0">
          <i className="fas fa-plus-circle me-2"></i>
          Submit New URL for Crawling
        </h5>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="row">
            <div className="col-md-6">
              <div className="mb-3">
                <label htmlFor="urlInput" className="form-label">Website URL</label>
                <input
                  type="url"
                  className="form-control"
                  id="urlInput"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com"
                  required
                  disabled={isSubmitting}
                />
                <div className="form-text">
                  Enter the URL you want to crawl and generate LLM text from.
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="mb-3">
                <label htmlFor="emailInput" className="form-label">Email (Optional)</label>
                <input
                  type="email"
                  className="form-control"
                  id="emailInput"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  disabled={isSubmitting}
                />
                <div className="form-text">
                  Get notified when content changes.
                </div>
              </div>
            </div>
            <div className="col-md-2">
              <div className="mb-3">
                <label className="form-label">&nbsp;</label>
                <button
                  type="submit"
                  className="btn btn-primary w-100"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? (
                    <>
                      <i className="fas fa-spinner fa-spin me-2"></i>
                      Submitting...
                    </>
                  ) : (
                    <>
                      <i className="fas fa-play me-2"></i>
                      Start Crawling
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UrlForm;



