import React, { useState, useEffect, useRef } from 'react';

function SafetyAnalysis() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  // Clean up preview URL on unmount or when preview changes
  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  const handleFileSelect = (selectedFile) => {
    if (selectedFile) {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
      setError(null);
    }
  };

  const handleInputChange = (e) => {
    const selectedFile = e.target.files && e.target.files[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files && e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleUploadAreaClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/safety/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorDetail = `Request failed with status ${response.status}`;
        try {
          const errData = await response.json();
          errorDetail = errData.detail || errData.message || JSON.stringify(errData);
        } catch {
          const errText = await response.text();
          if (errText) errorDetail = errText;
        }
        throw new Error(errorDetail);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        setResult(data.analysis || data.result || data.message || JSON.stringify(data, null, 2));
      } else {
        const text = await response.text();
        setResult(text);
      }
    } catch (err) {
      setError(err.message || 'An unexpected error occurred during safety analysis.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="safety-analysis">
      <h2>🦺 Safety Analysis</h2>
      <p className="description">
        Upload photos of your construction site to automatically inspect PPE compliance, hazardous zones, equipment safety, and potential OSHA violations.
      </p>

      <div
        className="upload-area"
        onClick={handleUploadAreaClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleUploadAreaClick();
          }
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          accept="image/*"
          style={{ display: 'none' }}
          onChange={handleInputChange}
        />
        <div className="upload-icon">📁</div>
        <p className="upload-text">Click or drag to upload a construction site image</p>
        <p className="upload-hint">Accepted formats: JPG, PNG, WEBP</p>
      </div>

      {preview && (
        <div className="preview-container">
          <h4>Image Preview:</h4>
          <img src={preview} alt="Construction site preview" className="image-preview" />
        </div>
      )}

      <div className="action-container">
        <button
          type="button"
          className="analyze-btn"
          onClick={handleAnalyze}
          disabled={!file || loading}
        >
          {loading ? 'Analyzing...' : 'Analyze Safety'}
        </button>
      </div>

      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Analyzing image...</p>
        </div>
      )}

      {error && (
        <div className="error-box">
          <p><strong>Error:</strong> {error}</p>
        </div>
      )}

      {result && (
        <div className="results-container">
          <h3>Analysis Results</h3>
          <div className="results-box" style={{ whiteSpace: 'pre-wrap' }}>
            {result}
          </div>
        </div>
      )}
    </div>
  );
}

export default SafetyAnalysis;
