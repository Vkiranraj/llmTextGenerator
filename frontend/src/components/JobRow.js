import React from 'react';
import StatusBadge from './StatusBadge';
import { jobService } from '../services/api';

const JobRow = ({ job, onJobUpdate, onError }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const handleRefreshJob = async () => {
    try {
      const updatedJob = await jobService.getJob(job.id);
      onJobUpdate(updatedJob);
    } catch (error) {
      console.error('Error refreshing job:', error);
      onError('Failed to refresh job');
    }
  };

  const handleShowError = () => {
    if (job.error_stack) {
      // You could implement a modal here or use a simple alert
      alert(`Error Details:\n\n${job.error_stack}`);
    }
  };

  const renderDownloadCell = () => {
    if (job.status === 'completed' && job.llm_text_content) {
      return (
        <a
          href={jobService.downloadJob(job.id)}
          className="btn btn-success btn-sm download-btn"
          download={`llm_${job.id}.txt`}
        >
          <i className="fas fa-download me-1"></i>
          Download
        </a>
      );
    } else if (job.status === 'completed') {
      return <span className="text-muted">No content</span>;
    } else {
      return <span className="text-muted">-</span>;
    }
  };

  const renderActionsCell = () => {
    let actions = [];

    if (job.status === 'error' && job.error_stack) {
      actions.push(
        <button
          key="error"
          className="btn btn-outline-danger btn-sm error-btn me-2"
          onClick={handleShowError}
        >
          <i className="fas fa-bug me-1"></i>
          View Error
        </button>
      );
    }

    if (job.status === 'completed' || job.status === 'error') {
      actions.push(
        <button
          key="refresh"
          className="btn btn-outline-secondary btn-sm"
          onClick={handleRefreshJob}
        >
          <i className="fas fa-sync me-1"></i>
          Refresh
        </button>
      );
    }

    return actions.length > 0 ? actions : <span className="text-muted">-</span>;
  };

  return (
    <tr id={`job-${job.id}`}>
      <td><strong>#{job.id}</strong></td>
      <td className="url-cell" title={job.url}>
        {job.url}
      </td>
      <td>
        <StatusBadge status={job.status} />
      </td>
      <td>{formatDate(job.created_at)}</td>
      <td>{formatDate(job.last_crawled)}</td>
      <td>{renderDownloadCell()}</td>
      <td>{renderActionsCell()}</td>
    </tr>
  );
};

export default JobRow;

