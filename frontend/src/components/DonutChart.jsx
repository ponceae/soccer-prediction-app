import {
  PieChart, 
  Pie, 
  Cell,
  Tooltip, 
  ResponsiveContainer, 
  Legend 
} from 'recharts';

export default function DonutChart({ 
  title, 
  data, 
  colors = ['#00a650', '#d1d1d1'] 
}) {
  return (
    <div className="chart-card">
      <h4 className="chart-title">{title}</h4>

      <div style={{ width: '100%', height: '220px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {data.map((_, index) =>(
                <Cell 
                  key={`cell-${index}`} fill={colors[index % colors.length]}
                />
              ))}
            </Pie>
            <Tooltip formatter={(value) => `${value}%`}/>
            <Legend verticalAlign="bottom" height={36}/>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
