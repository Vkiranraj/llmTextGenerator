# LLM Text Generator Frontend

A React application for submitting URLs and monitoring LLM text generation jobs. The interface provides real-time progress tracking and result downloads.

## Quick Start

### Local Development
```bash
cd frontend
npm install
npm start
```
Open `http://localhost:3000`

### Production Build
```bash
npm run build
```

## How It Works

The application follows a simple workflow:

1. **Submit URL**: Enter a website URL to crawl and generate LLM text
2. **Monitor Progress**: Watch real-time progress updates as the job processes
3. **View Results**: Download the generated text file when complete

The interface automatically handles job states - from submission through processing to completion or error handling.

## Project Structure

```
src/
├── components/
│   ├── UrlForm.js      # URL submission form
│   ├── ProgressView.js # Real-time progress display
│   ├── ResultsView.js  # Results and download interface
│   ├── Alert.js        # Notification messages
│   └── StatusBadge.js  # Status indicators
├── services/
│   └── api.js         # Backend API communication
├── App.js             # Main application logic
└── index.js           # Application entry point
```

## Components

**App.js** - Main component managing application state and user flow

**UrlForm.js** - Handles URL input validation and job creation

**ProgressView.js** - Displays job progress with real-time updates

**ResultsView.js** - Shows completed job results with download options

**Alert.js** - User notifications for success/error messages

**StatusBadge.js** - Visual status indicators for job states

## User Interaction

The application provides a streamlined experience:

- Submit a URL through the form
- Watch progress updates automatically refresh every 2 seconds
- Download results when processing completes
- Handle errors gracefully with clear messaging
- Start new jobs from any state

## API Integration

The frontend communicates with the backend through `services/api.js`:

- `createJob(url)` - Submit new URL for processing
- `getJobProgress(jobId)` - Fetch real-time job status
- `getJob(jobId)` - Retrieve complete job details
- `downloadJob(jobId)` - Get download URL for results

## Deployment

The application works in both local and production environments:

- **Local**: Connects to `http://localhost:8000` backend
- **Production**: Uses environment-based API endpoints
- **Docker**: Includes Dockerfile for containerized deployment

## Requirements

- Node.js 14+
- Backend API running (local or production)
- Modern web browser