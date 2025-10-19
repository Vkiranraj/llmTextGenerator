import React from 'react';

const StatusBadge = ({ status }) => {
  const statusConfig = {
    'pending': { class: 'status-pending', text: 'Pending', icon: 'fas fa-clock' },
    'in_progress': { class: 'status-in-progress', text: 'In Progress', icon: 'fas fa-spinner fa-spin' },
    'completed': { class: 'status-completed', text: 'Completed', icon: 'fas fa-check' },
    'error': { class: 'status-error', text: 'Error', icon: 'fas fa-exclamation-triangle' }
  };

  const config = statusConfig[status] || statusConfig['pending'];
  
  return (
    <span className={`status-badge ${config.class}`}>
      <i className={`${config.icon} me-1`}></i>
      {config.text}
    </span>
  );
};

export default StatusBadge;



