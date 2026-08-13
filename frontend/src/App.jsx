import { useState } from 'react';
import Navbar from "./components/Navbar";
import JobPosting_chart from "./components/JobpostedChart";
import "./App.css";

function App() {
  return (
    <div>
      <Navbar />
      <main className='dashboard'>
        <div className='grid-class'>
          <div className='job-posting-chart'>

            <JobPosting_chart />
          </div>

        </div>
      </main>

    </div>
  )
}


export default App
