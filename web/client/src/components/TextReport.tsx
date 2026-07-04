interface TextReportProps {
  report: {
    id: number;
    analysisId: number;
    textReport: string;
    csvPeopleUrl?: string | null;
    csvRelationshipsUrl?: string | null;
    networkGraphUrl?: string | null;
    createdAt: Date;
    updatedAt: Date;
  };
}

export default function TextReport({ report }: TextReportProps) {
  return (
    <div className="space-y-4">
      <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
        <pre className="text-sm text-slate-700 whitespace-pre-wrap font-mono overflow-auto max-h-96">
          {report.textReport}
        </pre>
      </div>
      <div className="text-xs text-slate-500">
        Generated: {new Date(report.createdAt).toLocaleString()}
      </div>
    </div>
  );
}
