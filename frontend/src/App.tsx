import UploadForm from './components/UploadForm'
import ResultsDisplay from './components/ResultsDisplay'
import ErrorDisplay from './components/ErrorDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import ResultsSkeleton from './components/ResultsSkeleton'
import Auth from './components/Auth'
import { useRecentUploads } from './hooks/useRecentUploads'
import { useAnalysis } from './hooks/useAnalysis'
import { useAuth } from './hooks/useAuth'

function App() {
  const { user, loading: authLoading, signOut } = useAuth()
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

  const handleSignOut = async () => {
    await signOut()
    window.location.reload() // Refresh to clear state
  }

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="app">
        <div className="loading-container">
          <LoadingSpinner uploadProgress={0} />
        </div>
      </div>
    )
  }

  // Show auth screen if not logged in
  if (!user) {
    return <Auth />
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div>
            <h1>Kinemotion</h1>
            <p>Video-based kinematic analysis for athletic performance</p>
          </div>
          <div className="user-info">
            <span className="user-email">{user.email}</span>
            <button onClick={handleSignOut} className="sign-out-button">
              Sign Out
            </button>
          </div>
        </div>
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
