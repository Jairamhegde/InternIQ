import { useState, useEffect } from 'react';
import { API_URL } from '../config';
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
import Loader from './Loader';
import { startCase } from 'lodash';

function TopRoles({ selectedField }) {
    const [rolesData, setRolesData] = useState([]);
    const [isLoading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        fetch(`${API_URL}/api/top-role-table?field=${selectedField?.value || 'all'}`)
            .then((response) => response.json())
            .then((data) => { setRolesData(data); setLoading(false); })
            .catch((error) => { console.log("Failed to fetch top roles", error); setLoading(false); });
    }, [selectedField]);

    return (
        <div className="top-roles-card">
            {isLoading ? (<Loader />) : (
                <>
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
                </>
            )}
        </div>
    );
}


function TopRoleChart({ selectedField }) {
    const [rolesData, setRolesData] = useState([]);
    const [isLoading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        fetch(`${API_URL}/api/top-role-table?field=${selectedField?.value || 'all'}`)
            .then((response) => response.json())
            .then((data) => { setRolesData(data); setLoading(false); })
            .catch((error) => { console.log("Failed to fetch top roles", error); setLoading(false); });
    }, [selectedField]);
    return (
        <div className='toprole-barchart'>
            {isLoading ? (<Loader />) : (
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
                                tickLine={false}
                                tick={{ fontSize: 12 }}
                                tickFormatter={startCase}


                            />

                            <Tooltip />
                            <Bar dataKey="volume" fill="#60a5fa" radius={[0, 6, 6, 0]} animationDuration={1300}
                            />

                        </BarChart>

                    </ResponsiveContainer>

                </div>
            )}
        </div>

    );
}


export default TopRoles;
export { TopRoleChart };

