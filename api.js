// api.js - Place this file in your project root
const API_URL = 'http://localhost:8000';

// Helper function to get token from localStorage
function getToken() {
    return localStorage.getItem('token');
}

// Helper function to get headers with authorization
function getHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
}

// Check if user is logged in
function isLoggedIn() {
    return !!getToken();
}

// Get current user role
function getUserRole() {
    return localStorage.getItem('role');
}

// Logout function
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    window.location.href = 'index.html';
}

// API calls
const API = {
    // Authentication
    async login(username, password) {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }
        
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('role', data.role);
        return data;
    },

    async getCurrentUser() {
        const response = await fetch(`${API_URL}/auth/me`, {
            headers: getHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to get user info');
        return await response.json();
    },

    // Complaints
    async createComplaint(category, subject, description) {
        const response = await fetch(`${API_URL}/complaints`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ category, subject, description })
        });
        
        if (!response.ok) throw new Error('Failed to create complaint');
        return await response.json();
    },

    async getComplaints() {
        const response = await fetch(`${API_URL}/complaints`, {
            headers: getHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to fetch complaints');
        return await response.json();
    },

    async updateComplaintStatus(complaintId, status) {
        const response = await fetch(`${API_URL}/complaints/${complaintId}`, {
            method: 'PATCH',
            headers: getHeaders(),
            body: JSON.stringify({ status })
        });
        
        if (!response.ok) throw new Error('Failed to update complaint');
        return await response.json();
    },

    // Certificates
    async getCertificates() {
        const response = await fetch(`${API_URL}/certificates`, {
            headers: getHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to fetch certificates');
        return await response.json();
    },

    async verifyCertificate(certNumber) {
        const response = await fetch(`${API_URL}/certificates/${certNumber}`);
        
        if (response.status === 404) {
            return null; // Certificate not found
        }
        
        if (!response.ok) throw new Error('Failed to verify certificate');
        return await response.json();
    },

    async createCertificate(farmerName, farmName, level, validUntil) {
        const response = await fetch(`${API_URL}/certificates`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ 
                farmer_name: farmerName, 
                farm_name: farmName, 
                level, 
                valid_until: validUntil 
            })
        });
        
        if (!response.ok) throw new Error('Failed to create certificate');
        return await response.json();
    },

    async revokeCertificate(certNumber) {
        const response = await fetch(`${API_URL}/certificates/${certNumber}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to revoke certificate');
        return await response.json();
    },

    // Ratings
    async submitRating(farmerId, transportRating, conditionsRating, equipmentRating, wagesRating, comments) {
        const response = await fetch(`${API_URL}/ratings`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                farmer_id: farmerId,
                transport_rating: transportRating,
                conditions_rating: conditionsRating,
                equipment_rating: equipmentRating,
                wages_rating: wagesRating,
                comments
            })
        });
        
        if (!response.ok) throw new Error('Failed to submit rating');
        return await response.json();
    },

    async getFarmerRatings(farmerId) {
        const response = await fetch(`${API_URL}/ratings/farmer/${farmerId}`, {
            headers: getHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to fetch ratings');
        return await response.json();
    },

    // Analytics
    async getAnalytics() {
        const response = await fetch(`${API_URL}/analytics/stats`, {
            headers: getHeaders()
        });
        
        if (!response.ok) throw new Error('Failed to fetch analytics');
        return await response.json();
    }
};

// Export for use in HTML files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API, isLoggedIn, getUserRole, logout, getToken };
}