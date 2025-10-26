import React, { useState, useEffect, useRef } from 'react';
import type { NetworkData, NetworkNode } from '../types';

interface Node extends NetworkNode {
    x: number;
    y: number;
    vx: number;
    vy: number;
}

interface Link {
    source: Node;
    target: Node;
    value: number;
}

interface NetworkGraphProps {
    data: NetworkData;
}

const colors = ["#4f46e5", "#4f46e5", "#10b981", "#f59e0b"]; // primary, source, internal, external

const ForceGraph: React.FC<{data: NetworkData, width: number, height: number}> = ({ data, width, height }) => {
    const [nodes, setNodes] = useState<Node[]>([]);
    const [links, setLinks] = useState<Link[]>([]);
    const [hoveredNode, setHoveredNode] = useState<Node | null>(null);

    // Fix: Initialize useRef with null to avoid potential issues with uninitialized refs.
    const simulationRef = useRef<number | null>(null);

    useEffect(() => {
        const newNodes: Node[] = data.nodes.map(node => ({
            ...node,
            x: node.fx ?? Math.random() * width,
            y: node.fy ?? Math.random() * height,
            vx: 0,
            vy: 0,
        }));

        const nodeMap = new Map(newNodes.map(node => [node.id, node]));

        const newLinks: Link[] = data.links
            .map(link => ({
                source: nodeMap.get(link.source)!,
                target: nodeMap.get(link.target)!,
                value: link.value,
            }))
            .filter(link => link.source && link.target);

        const tick = () => {
            const alpha = 0.03; // simulation cooling parameter

            // Apply forces
            for (const node of newNodes) {
                // Centering force
                node.vx += (width / 2 - node.x) * alpha * 0.05;
                node.vy += (height / 2 - node.y) * alpha * 0.05;

                // Repulsion force
                for (const otherNode of newNodes) {
                    if (node === otherNode) continue;
                    const dx = otherNode.x - node.x;
                    const dy = otherNode.y - node.y;
                    let distance = Math.sqrt(dx * dx + dy * dy);
                    if (distance < 1) distance = 1;
                    const force = -250 / (distance);
                    node.vx += (dx / distance) * force * alpha * 0.5;
                    node.vy += (dy / distance) * force * alpha * 0.5;
                }
            }

            // Link force
            for (const link of newLinks) {
                const dx = link.target.x - link.source.x;
                const dy = link.target.y - link.source.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                if (distance === 0) distance = 1;
                const desiredDistance = 200 - link.value;
                const force = (distance - desiredDistance) * 0.1 * alpha;
                const fx = (dx / distance) * force;
                const fy = (dy / distance) * force;
                
                if(!link.source.fx) { link.source.vx += fx; link.source.vy += fy; }
                if(!link.target.fx) { link.target.vx -= fx; link.target.vy -= fy; }
            }

            // Update positions
            for (const node of newNodes) {
                if(node.fx) node.x = node.fx;
                if(node.fy) node.y = node.fy;

                node.x += node.vx;
                node.y += node.vy;
                
                node.x = Math.max(15, Math.min(width - 15, node.x));
                node.y = Math.max(15, Math.min(height - 15, node.y));

                node.vx *= 0.98; // damping
                node.vy *= 0.98; // damping
            }

            setNodes([...newNodes]);
            setLinks([...newLinks]);

            simulationRef.current = requestAnimationFrame(tick);
        };

        simulationRef.current = requestAnimationFrame(tick);

        return () => {
            if (simulationRef.current) {
                cancelAnimationFrame(simulationRef.current);
            }
        };
    }, [data, width, height]);


    return (
        <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto' }}>
            <g>
                {links.map((link, i) => (
                    <line
                        key={i}
                        x1={link.source.x}
                        y1={link.source.y}
                        x2={link.target.x}
                        y2={link.target.y}
                        stroke="#9ca3af"
                        strokeWidth={Math.max(0.5, link.value / 30)}
                    />
                ))}
            </g>
            <g>
                {nodes.map((node) => (
                    <g key={node.id} transform={`translate(${node.x},${node.y})`} 
                        onMouseEnter={() => setHoveredNode(node)}
                        onMouseLeave={() => setHoveredNode(null)}
                        style={{ cursor: 'pointer' }}
                        >
                        <circle
                            r={node.group === 1 ? 15 : 10}
                            fill={colors[node.group]}
                            stroke="#fff"
                            strokeWidth={2.5}
                        />
                        <text
                            textAnchor="middle"
                            y={node.group === 1 ? 28 : -18}
                            fontSize="11px"
                            fontWeight="500"
                            fill="#374151"
                        >
                            {node.id}
                        </text>
                    </g>
                ))}
            </g>
             {hoveredNode && (
                <g transform={`translate(${hoveredNode.x}, ${hoveredNode.y})`} style={{ pointerEvents: 'none' }}>
                    <rect x={15} y={-25} width={150} height={hoveredNode.similarity ? 45 : 25} fill="rgba(255,255,255,0.95)" stroke="#e5e7eb" rx={4} />
                    <text x={23} y={-10} fontSize="12px" fontWeight="bold" fill="#1f2937">{hoveredNode.id}</text>
                    {hoveredNode.similarity && (
                         <text x={23} y={8} fontSize="12px" fill="#4f46e5">Similarity: {hoveredNode.similarity}%</text>
                    )}
                </g>
            )}
        </svg>
    );
};

export const NetworkGraph: React.FC<NetworkGraphProps> = ({ data }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const [size, setSize] = useState({ width: 0, height: 400 });

    useEffect(() => {
        const updateSize = () => {
            if (containerRef.current) {
                setSize({ width: containerRef.current.offsetWidth, height: 400 });
            }
        };
        const timeoutId = setTimeout(updateSize, 0);
        window.addEventListener('resize', updateSize);
        return () => {
            clearTimeout(timeoutId);
            window.removeEventListener('resize', updateSize);
        }
    }, []);

    return (
        <div ref={containerRef} className="w-full h-[400px] bg-gray-50 rounded-lg border">
            {size.width > 0 && <ForceGraph data={data} width={size.width} height={size.height} />}
        </div>
    );
};