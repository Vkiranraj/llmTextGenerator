import React from 'react';
import JobRow from './JobRow';

const JobsTable = ({ jobs, onJobUpdate, onError }) => {
  if (jobs.length === 0) {
    return (
      <div className="text-center py-5 text-muted">
        <i className="fas fa-inbox fa-3x mb-3"></i>
        <h5>No jobs yet</h5>
        <p>Submit a URL above to start crawling!</p>
      </div>
    );
  }

  // Sort jobs by creation date (newest first)
  const sortedJobs = [...jobs].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

  return (
    <div className="table-responsive">
      <table className="table table-hover">
        <thead className="table-light">
          <tr>
            <th>Job ID</th>
            <th>URL</th>
            <th>Status</th>
            <th>Created</th>
            <th>Last Updated</th>
            <th>Download</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {sortedJobs.map(job => (
            <JobRow
              key={job.id}
              job={job}
              onJobUpdate={onJobUpdate}
              onError={onError}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default JobsTable;

