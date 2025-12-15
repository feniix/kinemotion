import UploadForm from './components/UploadForm'
import ResultsDisplay from './components/ResultsDisplay'
import ErrorDisplay from './components/ErrorDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import ResultsSkeleton from './components/ResultsSkeleton'
import Auth from './components/Auth'
import LanguageSwitcher from './components/LanguageSwitcher'
import { useRecentUploads } from './hooks/useRecentUploads'
import { useAnalysis } from './hooks/useAnalysis'
import { useAuth } from './hooks/useAuth'
import { useBackendVersion } from './hooks/useBackendVersion'
import { useLanguage } from './hooks/useLanguage'

function App() {
  const { user, loading: authLoading, signOut } = useAuth()
  const { file, jumpType, loading, uploadProgress, metrics, error, enableDebug, setFile, setJumpType, setEnableDebug, analyze, retry } = useAnalysis()
  const { recentUploads, addRecentUpload, clearRecentUploads } = useRecentUploads()
  const { backendVersion, kinemotionVersion } = useBackendVersion()
  const { t } = useLanguage()

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
            <h1>{t('common.appName')}</h1>
            <p>{t('common.tagline')}</p>
          </div>
          <div className="user-info">
            <LanguageSwitcher />
            <span className="user-email">{user.email}</span>
            <button onClick={handleSignOut} className="sign-out-button">
              {t('header.signOut')}
            </button>
          </div>
        </div>
      </header>

      <main className="main">
        <UploadForm
          file={file}
          jumpType={jumpType}
          loading={loading}
          enableDebug={enableDebug}
          recentUploads={recentUploads}
          onFileChange={setFile}
          onJumpTypeChange={setJumpType}
          onEnableDebugChange={setEnableDebug}
          onAnalyze={handleAnalyze}
          onClearHistory={clearRecentUploads}
        />

        {loading && <LoadingSpinner uploadProgress={uploadProgress} />}
        {loading && uploadProgress >= 100 && <ResultsSkeleton />}
        {error && <ErrorDisplay error={error} onRetry={handleRetry} />}
        {metrics && !loading && <ResultsDisplay metrics={metrics} videoFile={file} />}
      </main>

      <footer className="footer">
        <p>
          {t('footer.copyright', { year: new Date().getFullYear() })} |
          <a href="https://github.com/feniix/kinemotion" target="_blank" rel="noopener noreferrer">
            {t('footer.github')}
          </a>
          {' | '}
          <span style={{ fontSize: '0.85em', opacity: 0.8 }}>
            Backend v{backendVersion} | Analysis v{kinemotionVersion}
          </span>
        </p>
      </footer>
    </div>
  )
}

export default App
