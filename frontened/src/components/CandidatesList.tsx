import { Users, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useQuery } from "@tanstack/react-query";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Candidate {
  id: string;
  filename: string;
}

const CandidatesList = () => {
  const { data, isLoading } = useQuery({
    queryKey: ["candidates"],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/debug/list_candidates?limit=50`);
      if (!response.ok) throw new Error("Failed to fetch candidates");
      return response.json() as Promise<Candidate[]>;
    },
  });

  return (
    <div className="max-w-4xl mx-auto">
      <Card className="shadow-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            All Candidates
          </CardTitle>
          <CardDescription>
            View all uploaded candidates in the database
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : data && data.length > 0 ? (
            <div className="space-y-2">
              {data.map((candidate, index) => (
                <div
                  key={candidate.id}
                  className="flex items-center gap-3 p-3 bg-secondary rounded-lg hover:bg-secondary/80 transition-colors"
                >
                  <span className="text-sm font-semibold text-muted-foreground min-w-[2rem]">
                    #{index + 1}
                  </span>
                  <span className="font-medium">{candidate.filename}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground">No candidates uploaded yet</p>
              <p className="text-sm text-muted-foreground mt-2">
                Upload resumes to get started
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CandidatesList;
