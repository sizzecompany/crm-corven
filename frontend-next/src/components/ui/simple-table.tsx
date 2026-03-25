export function SimpleTable({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <table className="w-full border-collapse overflow-hidden rounded border border-border text-sm">
      <thead className="bg-card">
        <tr>{headers.map((h) => <th key={h} className="border-b border-border px-3 py-2 text-left">{h}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((row, idx) => (
          <tr key={idx} className="odd:bg-[#0f1730]">
            {row.map((cell, i) => (
              <td key={`${idx}-${i}`} className="border-b border-border px-3 py-2">{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
