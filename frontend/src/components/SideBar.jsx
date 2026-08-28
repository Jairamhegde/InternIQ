import './SideBar.css'
import { useState, useEffect } from 'react';
import { API_URL } from '../config';

function Sidebar() {
    const [lastSync, setLastSync] = useState("Now")
    useEffect(() => {
        fetch(`${API_URL}/api/last-sync`)
            .then((response) => response.json())
            .then((res) => setLastSync(res.last_sync))
            .catch((error) => console.log("Failed to connect to last-sync", error))

    }, [])


    return (
        <aside className="sidebar">
            <div className='interniq-logo'>
                Intern<span>IQ</span>
            </div>
            <div className="nav-links">
                <a href="#market-overview">Market Overview</a>
                <a href="#comp-analysis">Comparative Analysis</a>
                <a href="#recent-market-trend">Recent Market Trends</a>
                <a href="#skill-gap-analysis">Skill Gap Analysis</a>
            </div>
            <div className="pipeline-status">
                <h3 className="pipeline-title">PIPELINE STATUS</h3>
                <div className="pipeline-info">
                    <span className="status-live"><span className="status-dot">●</span> LAST SYNC</span>
                    <span className="status-time">{lastSync}</span>
                </div>
            </div>
        </aside>
    );


}

export default Sidebar;