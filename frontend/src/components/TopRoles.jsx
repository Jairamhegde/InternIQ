import { useState, useEffect } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts';
import "./TopRoles.css"

function TopRoles() {
    const [rolesData, setRolesData] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/api/top-role-table')
            .then((response) => response.json())
            .then((data) => setRolesData(data))
            .catch((error) => console.log("Failed to fetch top roles", error));
    }, []);

    return (
        <div className="top-roles-card">
            <div className="top-roles-header">
                <h3>Top In-Demand Roles</h3>
            </div>

            <div className="table-responsive">
                <table className="top-roles-table">
                    <thead>
                        <tr>
                            <th>Role Profile</th>
                            <th className="align-right">Volume</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rolesData.map((item, index) => (
                            <tr key={index}>
                                <td className="role-name">{item.role}</td>
                                <td className="volume-val align-right">{item.volume}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}


function TopRoleChart() {
    const [rolesData, setRolesData] = useState([]);

    useEffect(() => {
        fetch('http://localhost:8000/api/top-role-table')
            .then((response) => response.json())
            .then((data) => setRolesData(data))
            .catch((error) => console.log("Failed to fetch top roles", error));
    }, []);
    return (
        <div className='toprole-barchart'>
            <div >
                <h3>Top Roles</h3>
                <ResponsiveContainer width="100%" height={350}>
                    <BarChart
                        data={rolesData}
                        layout='vertical'
                        margin={{
                            top: 10,
                            left: 30,
                            right: 30,
                            bottom: 10
                        }}
                    >

                        <XAxis type="number" />
                        <YAxis
                            dataKey='role'
                            type='category'
                            width={150}

                        />
                        <Tooltip />
                        <Bar dataKey="volume" fill="#2563eb"
                        />

                    </BarChart>

                </ResponsiveContainer>

            </div>
        </div>

    );
}


export default TopRoles;
export { TopRoleChart };

