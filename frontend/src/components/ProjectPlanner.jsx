import React, { useState } from 'react';

function ProjectPlanner() {
  const [formData, setFormData] = useState({
    projectName: '',
    projectType: 'Residential',
    startDate: new Date().toISOString().split('T')[0],
    duration: '',
    budget: '',
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const projectTypes = [
    'Residential',
    'Commercial',
    'Industrial',
    'Renovation',
    'Infrastructure',
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleGeneratePlan = async (e) => {
    e.preventDefault();

    if (!formData.projectName.trim()) {
      setError('Please provide a project name.');
      return;
    }
    if (!formData.startDate) {
      setError('Please select a project start date.');
      return;
    }
    if (!formData.duration || Number(formData.duration) <= 0) {
      setError('Please enter a valid project duration in days.');
      return;
    }
    if (!formData.budget || Number(formData.budget) <= 0) {
      setError('Please enter a valid project budget in ₹.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      project_name: formData.projectName.trim(),
      projectName: formData.projectName.trim(),
      project_type: formData.projectType,
      projectType: formData.projectType,
      start_date: formData.startDate,
      startDate: formData.startDate,
      duration: parseInt(formData.duration, 10),
      duration_days: parseInt(formData.duration, 10),
      budget: parseFloat(formData.budget),
    };

    try {
      const response = await fetch('http://localhost:8000/api/planning/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let errorDetail = `Planning request failed with status ${response.status}`;
        try {
          const errData = await response.json();
          errorDetail = errData.detail || errData.message || JSON.stringify(errData);
        } catch {
          const errText = await response.text();
          if (errText) errorDetail = errText;
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'An error occurred while generating the project plan.');
    } finally {
      setLoading(false);
    }
  };

  const scheduleList =
    result?.schedule ||
    result?.phases ||
    result?.timeline ||
    result?.plan ||
    [];

  return (
    <div className="project-planner">
      <h1 className="page-title">📋 Project Planner</h1>
      <p className="page-description">
        Generate structured milestone timelines, phase-wise schedules, and budget allocations
        for your construction initiative. Works deterministically without requiring an API key.
      </p>

      <div className="card">
        <form onSubmit={handleGeneratePlan}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="projectName">Project Name</label>
              <input
                id="projectName"
                type="text"
                name="projectName"
                value={formData.projectName}
                onChange={handleInputChange}
                placeholder="e.g. Skyline Residency Tower A"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="projectType">Project Type</label>
              <select
                id="projectType"
                name="projectType"
                value={formData.projectType}
                onChange={handleInputChange}
              >
                {projectTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="startDate">Start Date</label>
              <input
                id="startDate"
                type="date"
                name="startDate"
                value={formData.startDate}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="duration">Duration (days)</label>
              <input
                id="duration"
                type="number"
                name="duration"
                value={formData.duration}
                onChange={handleInputChange}
                placeholder="e.g. 180"
                min="1"
                step="1"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="budget">Budget (₹)</label>
              <input
                id="budget"
                type="number"
                name="budget"
                value={formData.budget}
                onChange={handleInputChange}
                placeholder="e.g. 5000000"
                min="1"
                step="any"
                required
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Plan'}
          </button>
        </form>

        {loading && (
          <div className="loading" style={{ marginTop: '20px' }}>
            <div className="spinner"></div>
            <span>Generating construction plan and schedule...</span>
          </div>
        )}

        {error && (
          <div className="error-box">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}
      </div>

      {result && (
        <div className="card results-box">
          <h3>Generated Project Plan</h3>

          <div className="project-summary">
            <div className="summary-item">
              <span className="label">Project Name</span>
              <span className="value">
                {result.project_name || result.projectName || formData.projectName}
              </span>
            </div>
            <div className="summary-item">
              <span className="label">Project Type</span>
              <span className="value">
                {result.project_type || result.projectType || formData.projectType}
              </span>
            </div>
            <div className="summary-item">
              <span className="label">Total Duration</span>
              <span className="value">
                {result.duration_days || result.duration || formData.duration} Days
              </span>
            </div>
            <div className="summary-item">
              <span className="label">Total Budget</span>
              <span className="value">
                {result.formatted_budget ||
                  (result.budget != null
                    ? `₹ ${Number(result.budget).toLocaleString('en-IN')}`
                    : `₹ ${Number(formData.budget).toLocaleString('en-IN')}`)}
              </span>
            </div>
          </div>

          <h4 style={{ marginTop: '24px', marginBottom: '12px', color: 'var(--gray-900)' }}>
            Phase Schedule & Timeline
          </h4>

          {scheduleList.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table className="schedule-table">
                <thead>
                  <tr>
                    <th>Phase</th>
                    <th>Duration (days)</th>
                    <th>Start Date</th>
                    <th>End Date</th>
                  </tr>
                </thead>
                <tbody>
                  {scheduleList.map((item, index) => (
                    <tr key={index}>
                      <td style={{ fontWeight: 500 }}>
                        {item.phase || item.name || item.phase_name || `Phase ${index + 1}`}
                      </td>
                      <td>{item.duration_days ?? item.duration ?? item.days ?? '-'}</td>
                      <td>{item.start_date || item.startDate || '-'}</td>
                      <td>{item.end_date || item.endDate || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ color: 'var(--gray-500)', fontSize: '0.9rem' }}>
              No detailed schedule breakdown available.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default ProjectPlanner;
