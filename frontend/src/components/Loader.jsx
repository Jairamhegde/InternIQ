
function Loader() {
    return (
        <div className="loader-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', minHeight: '150px', padding: '2rem' }}>
            <div className="spinner"></div>
            <span style={{ marginTop: '10px', color: '#64748b', fontSize: '0.9rem', fontWeight: '500' }}>Loading...</span>
        </div>
    )
}

export default Loader;
