import { 
  PolarAngleAxis,
  PolarGrid, 
  Radar, 
  RadarChart,  
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

export default function Strengths({ 
  radarData, 
  homeTeamName,
  awayTeamName,
  homeColor = "#3498D8",
  awayColor = "#E74C3C",
}) {
  return (
    <div className="chart-card strengths-card">
      <h3 className="chart-title-compact">Model Strengths</h3>
      <ResponsiveContainer width="100%" height={250}>
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
          <PolarGrid/>
          <PolarAngleAxis dataKey="metric" tick={{ fill: '#2C3E50', fontSize: 12 }}/>
          <Tooltip formatter={(value) => value.toFixed(2)}/>
          <Legend verticalAlign="bottom"/>
          <Radar 
            name={homeTeamName} 
            dataKey="homeValue" 
            stroke={homeColor} 
            fill={homeColor} 
            fillOpacity={0.5}
          />
          <Radar 
            name={awayTeamName} 
            dataKey="awayValue" 
            stroke={awayColor} 
            fill={awayColor}
            fillOpacity={0.5}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
