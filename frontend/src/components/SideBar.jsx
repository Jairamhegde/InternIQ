import './SideBar.css'

function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="nav-links">
                <a href="#market-overview">Market Overview</a>
                <a href="#comp-analysis">Comparative Analysis</a>
                <a href="#recent-market-trend">Recent Market Trends</a>
                <a href="#skill-gap-analysis">Skill Gap Analysis</a>
            </div>
        </aside>
    );


}

export default Sidebar;