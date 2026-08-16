
import "./Navbar.css";

function Navbar() {
    return (
        <nav>
            <h2 className="logo">
                Intern<span>IQ</span>
            </h2>
            <div>
                <a href="#market-overview">Market Overview</a>
                <a href="#comp-analysis">Comaparitive Analysis</a>
                <a href="#recent-market-trend">Recent Market Trends</a>
            </div>
        </nav>
    );

}


export default Navbar
