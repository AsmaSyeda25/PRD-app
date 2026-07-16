export interface Prd {
  productName: string;
  problemStatement: string;
  targetUsers: string;
  goals: string[];
  nonGoals: string[];
  requirements: string[];
  successMetrics: string[];
}

export const emptyPrd: Prd = {
  productName: "",
  problemStatement: "",
  targetUsers: "",
  goals: [""],
  nonGoals: [""],
  requirements: [""],
  successMetrics: [""],
};

export const STORAGE_KEY = "prd-builder:document";
