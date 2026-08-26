
import "./Navbar.css";

function Navbar() {
    return (
        <nav>
            <h2 className="logo">
                Intern<span>IQ</span>
            </h2>
            <div className="profile-container">
                {/* <h4>Jairam Hegde</h4> */}
                <button className="profile-btn" aria-label="Profile">

                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="profile-icon"
                    >
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                </button>
            </div>
        </nav>
    );

}

export default Navbar
