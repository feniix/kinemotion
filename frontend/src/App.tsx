import UploadForm from './components/UploadForm'
import ResultsDisplay from './components/ResultsDisplay'
import ErrorDisplay from './components/ErrorDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import ResultsSkeleton from './components/ResultsSkeleton'
import { useRecentUploads } from './hooks/useRecentUploads'
import { useAnalysis } from './hooks/useAnalysis'

function App() {
  const { file, jumpType, loading, uploadProgress, metrics, error, setFile, setJumpType, analyze, retry } = useAnalysis()
  const { recentUploads, addRecentUpload, clearRecentUploads } = useRecentUploads()

  const handleAnalyze = async () => {
    await analyze()
    // Save to recent uploads
    if (file) {
      addRecentUpload(file.name, jumpType)
    }
  }

  const handleRetry = async () => {
    await retry()
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Kinemotion</h1>
        <p>Video-based kinematic analysis for athletic performance</p>
      </header>

      <main className="main">
        <UploadForm
          file={file}
          jumpType={jumpType}
          loading={loading}
          recentUploads={recentUploads}
          onFileChange={setFile}
          onJumpTypeChange={setJumpType}
          onAnalyze={handleAnalyze}
          onClearHistory={clearRecentUploads}
        />

        {loading && <LoadingSpinner uploadProgress={uploadProgress} />}
        {loading && uploadProgress >= 100 && <ResultsSkeleton />}
        {error && <ErrorDisplay error={error} onRetry={handleRetry} />}
        {metrics && !loading && <ResultsDisplay metrics={metrics} />}
      </main>

      <footer className="footer">
        <p>
          Kinemotion &copy; {new Date().getFullYear()} |
          <a href="https://github.com/feniix/kinemotion" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App
