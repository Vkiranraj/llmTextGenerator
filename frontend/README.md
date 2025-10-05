# LLM Text Generator - React Frontend

This is the React frontend for the LLM Text Generator application. It provides a modern, responsive interface for submitting URLs and monitoring crawling jobs.

## Features

- **URL Submission**: Submit URLs for crawling and LLM text generation
- **Real-time Job Monitoring**: View job status, progress, and results
- **Auto-refresh**: Jobs automatically update every 3 seconds
- **Download Results**: Download generated LLM text files
- **Error Handling**: View detailed error information for failed jobs
- **Responsive Design**: Works on desktop and mobile devices

## Prerequisites

- Node.js (version 14 or higher)
- npm or yarn
- Backend API running on `http://localhost:8000`

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

1. Start the development server:
   ```bash
   npm start
   ```

2. Open your browser and navigate to `http://localhost:3000`

## Building for Production

To create a production build:

```bash
npm run build
```

The build files will be created in the `build` directory.

## Project Structure

```
src/
├── components/          # React components
│   ├── Alert.js        # Alert notification component
│   ├── JobRow.js       # Individual job row component
│   ├── JobsTable.js    # Jobs table component
│   ├── StatusBadge.js  # Job status badge component
│   └── UrlForm.js      # URL submission form component
├── services/           # API services
│   └── api.js         # API client and job service
├── App.js             # Main application component
├── index.js           # Application entry point
└── index.css          # Global styles
```

## Components

### App.js
Main application component that manages state and coordinates between other components.

### UrlForm.js
Form component for submitting new URLs for crawling.

### JobsTable.js
Table component that displays all crawling jobs with their status and actions.

### JobRow.js
Individual row component for each job, displaying job details and action buttons.

### StatusBadge.js
Component for displaying job status with appropriate styling and icons.

### Alert.js
Alert notification component for displaying success/error messages.

## API Integration

The frontend communicates with the backend API through the `services/api.js` file, which provides:

- `getJobs()`: Fetch all jobs
- `createJob(url)`: Create a new crawling job
- `getJob(jobId)`: Get a specific job
- `downloadJob(jobId)`: Get download URL for job results

## Styling

The application uses Bootstrap 5 for responsive design and includes custom CSS for:
- Status badges with color coding
- Loading animations
- Hover effects
- Responsive table design

## Features Comparison with Original

This React version maintains all the functionality of the original vanilla JavaScript version:

✅ URL submission with validation  
✅ Real-time job monitoring with auto-refresh  
✅ Job status tracking with visual indicators  
✅ Download functionality for completed jobs  
✅ Error handling and display  
✅ Responsive design  
✅ Loading states and user feedback  

## Development

The application uses React hooks for state management:
- `useState` for component state
- `useEffect` for side effects and lifecycle management
- `useCallback` for optimized function references

Polling is implemented using `setInterval` to automatically refresh job data every 3 seconds, with cleanup on component unmount.