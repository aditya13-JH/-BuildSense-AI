import React, { useState } from 'react';

function PropertyValuation() {
  const [formData, setFormData] = useState({
    city: '',
    property_type: 'Apartment',
    area: '',
    age: '',
    price_per_sq_ft: '',
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const propertyTypes = [
    'Apartment',
    'Independent House',
    'Villa',
    'Commercial',
    'Plot',
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCalculate = async (e) => {
    e.preventDefault();

    if (!formData.city.trim()) {
      setError('Please enter a city.');
      return;
    }
    if (!formData.area || Number(formData.area) <= 0) {
      setError('Please enter a valid property area in sq ft.');
      return;
    }
    if (formData.age === '' || Number(formData.age) < 0) {
      setError('Please enter a valid age of the property.');
      return;
    }
    if (!formData.price_per_sq_ft || Number(formData.price_per_sq_ft) <= 0) {
      setError('Please enter a valid price per sq ft.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {
      city: formData.city.trim(),
      property_type: formData.property_type,
      propertyType: formData.property_type,
      area: parseFloat(formData.area),
      area_sqft: parseFloat(formData.area),
      age: parseInt(formData.age, 10),
      age_years: parseInt(formData.age, 10),
      price_per_sq_ft: parseFloat(formData.price_per_sq_ft),
      price_per_sqft: parseFloat(formData.price_per_sq_ft),
    };

    try {
      const response = await fetch('http://localhost:8000/api/valuation/estimate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let errorDetail = `Calculation failed with status ${response.status}`;
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
      setError(err.message || 'An error occurred while calculating property valuation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="property-valuation">
      <h1 className="page-title">💰 Property Valuation</h1>
      <p className="page-description">
        Estimate the market value of residential or commercial properties based on location,
        property type, area, age, and baseline market rate. This tool operates instantly without an API key.
      </p>

      <div className="card">
        <form onSubmit={handleCalculate}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="city">City</label>
              <input
                id="city"
                type="text"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                placeholder="e.g. Mumbai, Bengaluru, Delhi"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="property_type">Property Type</label>
              <select
                id="property_type"
                name="property_type"
                value={formData.property_type}
                onChange={handleInputChange}
              >
                {propertyTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="area">Area (sq ft)</label>
              <input
                id="area"
                type="number"
                name="area"
                value={formData.area}
                onChange={handleInputChange}
                placeholder="e.g. 1200"
                min="1"
                step="any"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="age">Age of Property (years)</label>
              <input
                id="age"
                type="number"
                name="age"
                value={formData.age}
                onChange={handleInputChange}
                placeholder="e.g. 5"
                min="0"
                step="1"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="price_per_sq_ft">Price per sq ft (₹)</label>
              <input
                id="price_per_sq_ft"
                type="number"
                name="price_per_sq_ft"
                value={formData.price_per_sq_ft}
                onChange={handleInputChange}
                placeholder="e.g. 8500"
                min="1"
                step="any"
                required
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Calculating...' : 'Calculate Valuation'}
          </button>
        </form>

        {loading && (
          <div className="loading" style={{ marginTop: '20px' }}>
            <div className="spinner"></div>
            <span>Calculating property valuation...</span>
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
          <h3>Valuation Assessment</h3>
          <div className="valuation-result">
            <span className="value-label">Estimated Market Value</span>
            <div className="estimated-value">
              {result.formatted_value ||
                (result.estimated_value != null
                  ? `₹ ${Number(result.estimated_value).toLocaleString('en-IN')}`
                  : 'N/A')}
            </div>

            <div className="valuation-details">
              <div className="detail-item">
                <span className="label">City</span>
                <span className="value">{formData.city}</span>
              </div>
              <div className="detail-item">
                <span className="label">Property Type</span>
                <span className="value">{formData.property_type}</span>
              </div>
              <div className="detail-item">
                <span className="label">Area</span>
                <span className="value">{Number(formData.area).toLocaleString('en-IN')} sq ft</span>
              </div>
              <div className="detail-item">
                <span className="label">Age of Property</span>
                <span className="value">{formData.age} {Number(formData.age) === 1 ? 'year' : 'years'}</span>
              </div>
              <div className="detail-item">
                <span className="label">Price per sq ft</span>
                <span className="value">₹ {Number(formData.price_per_sq_ft).toLocaleString('en-IN')}</span>
              </div>
              {result.depreciation_factor != null && (
                <div className="detail-item">
                  <span className="label">Depreciation Applied</span>
                  <span className="value">{(Number(result.depreciation_factor) * 100).toFixed(1)}%</span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PropertyValuation;
