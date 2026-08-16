import { useState } from 'react';
import Navbar from "./components/Navbar";
import JobPosting_chart from "./components/JobpostedChart";
import Key_insights from "./components/KeyInsights"
import MarketOverview from './components/MarketOverview';
import TopRoles, { TopRoleChart } from "./components/TopRoles";
import ComparitiveAnalysis from "./components/ComparitiveAnalysis";
import RecentMarketTrend from "./components/RecentMarketTrend";

import "./App.css";

function App() {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [data, setData] = useState({})
  const [selectedField, setField] = useState({ value: 'all', label: 'All' })

  return (
    <div>
      <Navbar />
      <main className='dashboard'>
        <section id='market-overview' className='market-overview-section'>
          <MarketOverview data={data} setData={setData} selectedField={selectedField} setField={setField} />
          <div className='grid-class'>
            <div className='job-posting-chart' style={{ display: 'flex', gap: '2px' }}>
              <JobPosting_chart selectedYear={selectedYear} setSelectedYear={setSelectedYear} />
              <Key_insights selectedYear={selectedYear} data={data} />
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

        <section id='recent-market-trend'>
          <RecentMarketTrend />
        </section>



      </main>
    </div>
  )
}


export default App
