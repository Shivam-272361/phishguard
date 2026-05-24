import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './AdminDashboard.css';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalScans: 0,
    phishingDetected: 0,
    activeUsers: 0,
    premiumUsers: 0
  });
  const [recentThreats, setRecentThreats] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const statsRes = await api.get('/admin/stats');
      const threatsRes = await api.get('/admin/recent-threats');
      const usersRes = await api.get('/admin/users');
      
      setStats(statsRes.data);
      setRecentThreats(threatsRes.data);
      setUsers(usersRes.data);
    } catch (error) {
      console.error("Error fetching admin data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="admin-loading">Loading Admin Console...</div>;

  return (
    <div className="admin-container">
      <header className="admin-header">
        <h1>Admin Analytics Dashboard</h1>
        <p>Real-time oversight of PhishGuard AI Ecosystem</p>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Scans</h3>
          <p className="stat-value">{stats.totalScans}</p>
        </div>
        <div className="stat-card danger">
          <h3>Phishing Detected</h3>
          <p className="stat-value">{stats.phishingDetected}</p>
        </div>
        <div className="stat-card">
          <h3>Active Users</h3>
          <p className="stat-value">{stats.activeUsers}</p>
        </div>
        <div className="stat-card premium">
          <h3>Premium Plans</h3>
          <p className="stat-value">{stats.premiumUsers}</p>
        </div>
      </div>

      <div className="admin-content-split">
        <section className="admin-section">
          <h2>Recent High-Risk Threats</h2>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Target</th>
                  <th>Type</th>
                  <th>Score</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {recentThreats.map((threat, index) => (
                  <tr key={index}>
                    <td>{threat.target}</td>
                    <td><span className={`tag ${threat.type}`}>{threat.type}</span></td>
                    <td><span className="risk-score">{threat.score}%</span></td>
                    <td>{new Date(threat.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="admin-section">
          <h2>User Management</h2>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>User</th>
                  <th>Plan</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user, index) => (
                  <tr key={index}>
                    <td>{user.email}</td>
                    <td>{user.plan}</td>
                    <td><span className={`status-dot ${user.status}`}></span> {user.status}</td>
                    <td>
                      <button className="manage-btn">Manage</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};

export default AdminDashboard;
