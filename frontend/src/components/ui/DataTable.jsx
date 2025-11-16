import Card from './Card'

const DataTable = ({ 
  headers, 
  data, 
  renderRow, 
  emptyMessage = 'No data available',
  className = ''
}) => {
  return (
    <Card className={`overflow-hidden p-0 ${className}`}>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {headers.map((header, idx) => (
                <th
                  key={idx}
                  className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider"
                >
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.length === 0 ? (
              <tr>
                <td colSpan={headers.length} className="px-6 py-8 text-center text-gray-500">
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              data.map((row, idx) => (
                <tr key={idx} className="hover:bg-gray-50 transition-colors">
                  {renderRow(row, idx)}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </Card>
  )
}

export default DataTable

