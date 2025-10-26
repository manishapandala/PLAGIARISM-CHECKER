
import React, { useMemo, useState } from 'react';
import type { CheckResult, VisualizationData, NetworkData, NetworkNode, NetworkLink } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { NetworkGraph } from './NetworkGraph';

interface VisualizationsProps {
    results: CheckResult;
    sourceDocId: string;
}

const getLevelClasses = (level: string) => {
    switch (level) {
        case 'exact':
        case 'high':
            return 'bg-red-200 text-red-900';
        case 'moderate':
            return 'bg-orange-200 text-orange-900';
        case 'low':
            return 'bg-yellow-200 text-yellow-900';
        default:
            return 'bg-gray-100';
    }
};

const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-white p-3 border border-gray-300 rounded-lg shadow-lg">
                <p className="font-bold text-gray-800">{label}</p>
                <p className="text-sm text-primary">{`Similarity: ${payload[0].value}%`}</p>
            </div>
        );
    }
    return null;
};

const SortIndicator = ({ direction }: { direction: 'asc' | 'desc' | 'none' }) => {
    if (direction === 'none') return null;
    return <span className="ml-1">{direction === 'asc' ? '▲' : '▼'}</span>;
};


export const Visualizations: React.FC<VisualizationsProps> = ({ results, sourceDocId }) => {
    const [activeTab, setActiveTab] = useState<'chart' | 'heatmap' | 'network'>('chart');
    const [sortConfig, setSortConfig] = useState<{ key: keyof VisualizationData; direction: 'asc' | 'desc' } | null>({ key: 'similarity', direction: 'desc' });

    const chartData = useMemo(() => {
        return [...results.similarities]
            .sort((a, b) => b.similarity_score - a.similarity_score)
            .map(sim => ({
                name: sim.matched_doc_id,
                'Similarity (%)': Math.round(sim.similarity_score),
            }));
    }, [results]);
    
    const heatmapData: VisualizationData[] = useMemo(() => {
        return results.similarities.map(sim => ({
            doc_id: sim.matched_doc_id,
            similarity: Math.round(sim.similarity_score),
            matched_segments: sim.matched_lines.length,
            level: sim.similarity_level,
        }));
    }, [results]);

    const sortedHeatmapData = useMemo(() => {
        let sortableItems = [...heatmapData];
        if (sortConfig !== null) {
            sortableItems.sort((a, b) => {
                if (a[sortConfig.key] < b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? -1 : 1;
                }
                if (a[sortConfig.key] > b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? 1 : -1;
                }
                return 0;
            });
        }
        return sortableItems;
    }, [heatmapData, sortConfig]);

     const requestSort = (key: keyof VisualizationData) => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    const networkData: NetworkData = useMemo(() => {
        const nodes: NetworkNode[] = [{ id: sourceDocId, group: 1, fx: 250, fy: 200 }];
        const links: NetworkLink[] = [];

        results.similarities.forEach(sim => {
            nodes.push({
                id: sim.matched_doc_id,
                group: sim.type === 'internal' ? 2 : 3,
                similarity: Math.round(sim.similarity_score)
            });
            links.push({
                source: sourceDocId,
                target: sim.matched_doc_id,
                value: sim.similarity_score
            });
        });
        return { nodes, links };
    }, [results, sourceDocId]);


    if(results.similarities.length === 0) {
        return <div className="text-center py-10 text-gray-500">No data available for visualization.</div>
    }

    const renderContent = () => {
        switch (activeTab) {
            case 'chart':
                return (
                     <div>
                        <h4 className="text-lg font-bold text-gray-800 mb-4">Similarity Score Distribution</h4>
                        <div style={{ width: '100%', height: 400 }}>
                            <ResponsiveContainer>
                                <BarChart
                                    data={chartData}
                                    margin={{ top: 5, right: 20, left: -10, bottom: 50 }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" tick={{ fontSize: 12 }} angle={-45} textAnchor="end" interval={0} />
                                    <YAxis />
                                    <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(79, 70, 229, 0.1)' }} />
                                    <Legend />
                                    <Bar dataKey="Similarity (%)" fill="#4f46e5" barSize={30} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                );
            case 'heatmap':
                 return (
                    <div>
                        <h4 className="text-lg font-bold text-gray-800 mb-4">Similarity Details</h4>
                        <div className="overflow-x-auto border border-gray-200 rounded-lg">
                            <table className="min-w-full bg-white">
                                <thead className="bg-gray-50">
                                    <tr>
                                        {['doc_id', 'similarity', 'matched_segments', 'level'].map((key) => (
                                            <th key={key} className="py-3 px-4 border-b text-left text-sm font-semibold text-gray-600 cursor-pointer" onClick={() => requestSort(key as keyof VisualizationData)}>
                                                {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                                <SortIndicator direction={sortConfig?.key === key ? sortConfig.direction : 'none'} />
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {sortedHeatmapData.map(item => (
                                        <tr key={item.doc_id} className="hover:bg-gray-50">
                                            <td className="py-2 px-4 border-b text-sm text-gray-700 font-medium">{item.doc_id}</td>
                                            <td className={`py-2 px-4 border-b text-sm font-semibold text-center ${getLevelClasses(item.level)}`}>{item.similarity}%</td>
                                            <td className="py-2 px-4 border-b text-sm text-gray-700 text-center">{item.matched_segments}</td>
                                            <td className="py-2 px-4 border-b text-sm text-gray-700 capitalize">{item.level}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                );
            case 'network':
                return (
                    <div>
                        <h4 className="text-lg font-bold text-gray-800 mb-4">Document Similarity Network</h4>
                         <NetworkGraph data={networkData} />
                    </div>
                );
        }
    }

    const tabs = [
        { id: 'chart', name: 'Distribution Chart' },
        { id: 'heatmap', name: 'Details Table' },
        { id: 'network', name: 'Network Graph' }
    ];

    return (
         <div className="space-y-6">
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-6" aria-label="Tabs">
                     {tabs.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as any)}
                            className={`whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm ${activeTab === tab.id ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
                        >
                            {tab.name}
                        </button>
                     ))}
                </nav>
            </div>
            <div className="pt-2 min-h-[450px]">
                {renderContent()}
            </div>
        </div>
    );
};
