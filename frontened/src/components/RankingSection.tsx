import { useState } from "react";
import { Search, Trophy, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { useMutation } from "@tanstack/react-query";
import CandidateCard from "./CandidateCard";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface RankedCandidate {
  candidate_id: string;
  filename: string;
  score: number;
  name: string;
  phone: string;
  email: string;
  links: string;
  summary: string;
  education: string;
  skills: string;
  experience: string;
}

const RankingSection = () => {
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [results, setResults] = useState<RankedCandidate[]>([]);
  const { toast } = useToast();

  const rankMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_URL}/rank`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          title: jobTitle,
          description: jobDescription,
        }),
      });

      if (!response.ok) {
        throw new Error("Ranking failed");
      }

      return response.json();
    },
    onSuccess: (data) => {
      setResults(data.results);
      toast({
        title: "Ranking Complete",
        description: `Found ${data.results.length} matching candidates`,
      });
    },
    onError: () => {
      toast({
        title: "Ranking Failed",
        description: "Failed to rank candidates. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleRank = () => {
    if (!jobTitle.trim() || !jobDescription.trim()) {
      toast({
        title: "Missing Information",
        description: "Please provide both job title and description",
        variant: "destructive",
      });
      return;
    }
    rankMutation.mutate();
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <Card className="shadow-card hover:shadow-hover transition-shadow duration-300">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5 text-primary" />
            Job Description
          </CardTitle>
          <CardDescription>
            Enter the job details to find the best matching candidates
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="job-title">Job Title</Label>
            <Input
              id="job-title"
              placeholder="e.g., Senior Software Engineer"
              value={jobTitle}
              onChange={(e) => setJobTitle(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="job-description">Job Description</Label>
            <Textarea
              id="job-description"
              placeholder="Paste the full job description here, including required skills, experience, and qualifications..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={8}
              className="resize-none"
            />
          </div>

          <Button
            onClick={handleRank}
            disabled={rankMutation.isPending}
            className="w-full bg-gradient-primary hover:opacity-90"
            size="lg"
          >
            {rankMutation.isPending ? (
              <>
                <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                Analyzing Candidates...
              </>
            ) : (
              <>
                <Search className="h-5 w-5 mr-2" />
                Rank Candidates
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-4 animate-fade-in">
          <div className="flex items-center gap-2 text-lg font-semibold">
            <Trophy className="h-5 w-5 text-primary" />
            Top Candidates ({results.length})
          </div>
          <div className="space-y-4">
            {results.map((candidate, index) => (
              <CandidateCard
                key={candidate.candidate_id}
                candidate={candidate}
                rank={index + 1}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RankingSection;
