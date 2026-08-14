import { useState } from 'react';
import Navbar from "./components/Navbar";
import JobPosting_chart from "./components/JobpostedChart";
import Key_insights from "./components/KeyInsights"
import MarketOverview from './components/MarketOverview';
import TopRoles, { TopRoleChart } from "./components/TopRoles"
import ComparitiveAnalysis from "./components/ComparitiveAnalysis"
import "./App.css";

function App() {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  return (
    <div>
      <Navbar />
      <main className='dashboard'>
        <section id='market-overview' className='market-overview-section'>
          <MarketOverview />
          <div className='grid-class'>
            <div className='job-posting-chart' style={{ display: 'flex', gap: '2px' }}>
              <JobPosting_chart selectedYear={selectedYear} setSelectedYear={setSelectedYear} />
              <Key_insights selectedYear={selectedYear} />
            </div>
          </div>
          <div className='top-role-charts' style={{ display: 'flex', gap: '24px' }}>
            <TopRoles />
            <TopRoleChart />
          </div>
        </section>

        <section id="comp-analysis" className='comparitive-analysis-secttion'>
          <ComparitiveAnalysis />


        </section>



      </main>
    </div>
  )
}


export default App
