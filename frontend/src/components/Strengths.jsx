import { 
  PolarAngleAxis,
  PolarGrid, 
  Radar, 
  RadarChart,  
  ResponsiveContainer,
  Tooltip,
} from "recharts";

export default function Strengths({ radarData, teamName }) {
  return (
    <div className="chart-card strengths-card">
      <h3 className="chart-title-compact">Model Strengths</h3>
      <ResponsiveContainer width="100%" height={250}>
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
          <PolarGrid/>
          <PolarAngleAxis dataKey="metric" tick={{ fill: '#2C3E50', fontSize: 12 }}/>
          <Tooltip/>
          <Radar 
            name={teamName} 
            dataKey="value" 
            stroke="#3498DB" 
            fill="#3498DB" 
            fillOpacity={0.5}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
