import { useState } from "react";
import { ChevronDown, Award, Briefcase, GraduationCap, Code, FileText } from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

// Render resume text smartly: detect bullets or numbered lines and show as a proper list
const renderRichText = (text?: string): JSX.Element | null => {
  if (!text) return null;
  const normalized = text.replace(/\r\n/g, "\n").trim();

  // Split by newlines first to check structure
  const lines = normalized.split(/\n+/);
  const bulletLineRegex = /^\s*(?:[•\-–—*○◦]\s+|\d+\.\s+)/;
  
  // Check if most lines start with bullets (structured list)
  const bulletLines = lines.filter(l => bulletLineRegex.test(l.trim()));
  const isStructuredList = bulletLines.length > 0 && bulletLines.length >= lines.length * 0.3;

  if (isStructuredList) {
    // Render as a structured bullet list
    const items = lines
      .map(l => l.trim())
      .filter(Boolean)
      .map(l => l.replace(bulletLineRegex, "").trim())
      .filter(Boolean);

    return (
      <ul className="list-disc pl-6 space-y-1">
        {items.map((item, idx) => (
          <li key={idx} className="text-sm text-muted-foreground">
            {item}
          </li>
        ))}
      </ul>
    );
  }

  // Check for inline bullets (e.g., "text ○ item1 ○ item2 ○ item3")
  const inlineBulletRegex = /[•◦○]/;
  if (inlineBulletRegex.test(normalized)) {
    // Split by bullet characters
    const parts = normalized.split(inlineBulletRegex).map(s => s.trim()).filter(Boolean);
    
    // If we have multiple parts, render as list
    if (parts.length >= 3) {
      return (
        <ul className="list-disc pl-6 space-y-1">
          {parts.map((item, idx) => (
            <li key={idx} className="text-sm text-muted-foreground">
              {item}
            </li>
          ))}
        </ul>
      );
    }
  }

  // Fallback: render as paragraphs with preserved whitespace
  const blocks = lines.map((line, idx) => {
    const trimmed = line.trim();
    if (!trimmed) return null;
    
    // Check if this line has a bullet
    if (bulletLineRegex.test(trimmed)) {
      const content = trimmed.replace(bulletLineRegex, "").trim();
      return (
        <div key={idx} className="flex items-start gap-2">
          <span className="text-muted-foreground mt-0.5">•</span>
          <span className="text-sm text-muted-foreground flex-1">{content}</span>
        </div>
      );
    }
    
    return (
      <p key={idx} className="text-sm text-muted-foreground">
        {trimmed}
      </p>
    );
  }).filter(Boolean);

  return <div className="space-y-1">{blocks}</div>;
};

interface CandidateCardProps {
  candidate: {
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
  };
  rank: number;
}

const getScoreColor = (score: number) => {
  if (score >= 0.8) return "text-success";
  if (score >= 0.6) return "text-primary";
  return "text-muted-foreground";
};

const getScoreBg = (score: number) => {
  if (score >= 0.8) return "bg-success/10 border-success/20";
  if (score >= 0.6) return "bg-primary/10 border-primary/20";
  return "bg-muted border-border";
};

const CandidateCard = ({ candidate, rank }: CandidateCardProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const scorePercentage = (candidate.score * 100).toFixed(1);

  return (
    <Card className="shadow-card hover:shadow-hover transition-all duration-300">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-4 flex-1">
            <div className={`flex items-center justify-center w-12 h-12 rounded-full ${getScoreBg(candidate.score)} border`}>
              <span className="text-lg font-bold">#{rank}</span>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-lg font-semibold">
                  {candidate.name || candidate.filename || `Candidate ${candidate.candidate_id.slice(0, 8)}`}
                </h3>
                <Badge variant="outline" className="font-mono text-xs">
                  {candidate.candidate_id.slice(0, 8)}
                </Badge>
              </div>
              {(candidate.email || candidate.phone) && (
                <div className="text-sm text-muted-foreground space-y-0.5">
                  {candidate.email && <div>{candidate.email}</div>}
                  {candidate.phone && <div>{candidate.phone}</div>}
                </div>
              )}
              <div className="flex items-center gap-2">
                <Award className={`h-4 w-4 ${getScoreColor(candidate.score)}`} />
                <span className={`text-2xl font-bold ${getScoreColor(candidate.score)}`}>
                  {scorePercentage}%
                </span>
                <span className="text-sm text-muted-foreground">match score</span>
              </div>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Quick Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {candidate.skills && (
            <div className="p-3 bg-secondary rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Code className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">Skills</span>
              </div>
              <div className="text-sm text-muted-foreground line-clamp-3">
                {renderRichText(candidate.skills)}
              </div>
            </div>
          )}
          {candidate.experience && (
            <div className="p-3 bg-secondary rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Briefcase className="h-4 w-4 text-primary" />
                <span className="text-sm font-medium">Experience</span>
              </div>
              <div className="text-sm text-muted-foreground line-clamp-3">
                {renderRichText(candidate.experience)}
              </div>
            </div>
          )}
        </div>

        {/* Expandable Details */}
        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <CollapsibleTrigger asChild>
            <Button variant="outline" className="w-full">
              <ChevronDown className={`h-4 w-4 mr-2 transition-transform ${isOpen ? "rotate-180" : ""}`} />
              {isOpen ? "Hide Details" : "Show Full Details"}
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="space-y-4 mt-4">
            {candidate.summary && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-primary" />
                  <h4 className="font-medium">Summary</h4>
                </div>
                <div className="pl-6">
                  {renderRichText(candidate.summary)}
                </div>
              </div>
            )}
            {candidate.education && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <GraduationCap className="h-4 w-4 text-primary" />
                  <h4 className="font-medium">Education</h4>
                </div>
                <div className="pl-6">
                  {renderRichText(candidate.education)}
                </div>
              </div>
            )}
            {candidate.skills && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Code className="h-4 w-4 text-primary" />
                  <h4 className="font-medium">Skills</h4>
                </div>
                <div className="pl-6">
                  {renderRichText(candidate.skills)}
                </div>
              </div>
            )}
            {candidate.experience && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <Briefcase className="h-4 w-4 text-primary" />
                  <h4 className="font-medium">Experience</h4>
                </div>
                <div className="pl-6">
                  {renderRichText(candidate.experience)}
                </div>
              </div>
            )}
          </CollapsibleContent>
        </Collapsible>
      </CardContent>
    </Card>
  );
};

export default CandidateCard;
