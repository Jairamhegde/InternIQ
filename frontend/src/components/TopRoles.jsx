import { API_URL } from '../config.js';
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
import { useQuery } from '@tanstack/react-query';

function TopRoles({ selectedField }) {

    const { data: rolesData = [], isLoading, isError } = useQuery({
        queryKey: ['top-role-table', selectedField?.value],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/top-role-table?field=${selectedField?.value || 'all'}`)
            if (!response.ok) {
                throw new Error("Network response not ok");
            }
            return response.json();
        }
    })
    if (isError) {
        console.log("failed to connect to top-role-table.")
    }

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
                                        <td className="role-name">
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" style={{ width: '18px', height: '18px', color: '#27da48ff' }}>
                                                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941" />
                                                </svg>
                                                {item.role}
                                            </div>
                                        </td>
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
    const { data: rolesData = [], isLoading } = useQuery({
        queryKey: ['top-role-table', selectedField?.value],
        queryFn: async () => {
            const response = await fetch(`${API_URL}/api/top-role-table?field=${selectedField?.value || 'all'}`)
            if (!response.ok) throw new Error("Network response not ok");
            return response.json();
        }
    });

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

