import { 
  Bar,  
  BarChart, 
  ResponsiveContainer, 
  Tooltip,
  XAxis, 
  YAxis,
} from "recharts";

export default function Outcomes({ outcomeData }) {
  return (
    <div className="chart-card outcomes-card">
      <h3 className="chart-title">Outcome Probabilities</h3>
      <ResponsiveContainer width="100%" height={100}>
        <BarChart layout="vertical" data={outcomeData} stackOffset="expand">
          <XAxis type="number" hide/>
          <YAxis type="category" dataKey="name" hide/>
          <Tooltip formatter={(value) => `${value}%`}/>
          <Bar dataKey="Win" stackId="a" fill="#2ECC71"/>
          <Bar dataKey="Draw" stackId="a" fill="#95A5A6"/>
          <Bar dataKey="Loss" stackId="a" fill="#E74C3C"/>
        </BarChart>
      </ResponsiveContainer>

      <div className="bar-legend">
        <span><strong className="legend-win">Win:</strong>{outcomeData[0].Win}%</span>
        <span><strong className="legend-draw">Draw:</strong>{outcomeData[0].Draw}%</span>
        <span><strong className="legend-loss">Loss:</strong>{outcomeData[0].Loss}%</span>
      </div>
    </div>
  );
}