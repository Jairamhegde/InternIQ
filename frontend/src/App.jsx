import { useState } from 'react';
import Navbar from "./components/Navbar";
import JobPosting_chart from "./components/JobpostedChart";
import Key_insights from "./components/KeyInsights"
import MarketOverview from './components/MarketOverview';
import TopRoles, { TopRoleChart } from "./components/TopRoles";
import ComparitiveAnalysis from "./components/ComparitiveAnalysis";
import RecentMarketTrend from "./components/RecentMarketTrend";
import SkillgapAnalysis from './components/SkillgapAnalysis';
import "./App.css";
import Sidebar from './components/SideBar';

function App() {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [data, setData] = useState({})
  const [selectedField, setField] = useState({ value: 'all', label: 'All' })

  return (
    <div>
      <Navbar />
      <div className='app-body'>
        <div className='sidebar-div'>
          <Sidebar />

        </div>

        <main className='dashboard'>
          <section id='market-overview' className='market-overview-section'>
            <MarketOverview data={data} setData={setData} selectedField={selectedField} setField={setField} />
            <div className='grid-class'>
              <div className='job-posting-chart' style={{ display: 'flex', gap: '2px' }}>
                <JobPosting_chart selectedYear={selectedYear} setSelectedYear={setSelectedYear} selectedField={selectedField} />
                <Key_insights selectedYear={selectedYear} data={data} selectedField={selectedField} />
              </div>
            </div>
            <div className='top-role-charts' style={{ display: 'flex', gap: '24px' }}>
              <TopRoles selectedField={selectedField} />
              <TopRoleChart selectedField={selectedField} />
            </div>
          </section>

          <section id="comp-analysis" className='comparitive-analysis-secttion'>
            <ComparitiveAnalysis />
          </section>

          <section id='recent-market-trend'>
            <RecentMarketTrend />
          </section>

          <section id='skill-gap-analysis'>
            <SkillgapAnalysis />
          </section>


        </main>
      </div>

    </div>


  )
}


export default App
