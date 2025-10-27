import { z } from "zod";

export const contextSchema = z.object({
  entityType: z.string().min(1, "Entity type is required"),
  jurisdiction: z.string().min(1, "Jurisdiction is required"),
  yearEnd: z.string().regex(/^\d{4}-\d{2}-\d{2}$/u, "Year end must be YYYY-MM-DD"),
  framework: z.string().min(1, "Reporting framework is required")
});

export const uploadSchema = z.object({
  clientId: z.string().min(1),
  fileId: z.string().min(1),
  fileType: z.enum(["csv", "xlsx", "zip"])
});

export const mappingSchema = z.object({
  tbId: z.string().min(1),
  confidenceThreshold: z.number().min(0).max(1)
});

export const templateSchema = z.object({
  jurisdiction: z.string().min(1),
  entityType: z.string().min(1),
  framework: z.string().min(1)
});

export const draftSchema = z.object({
  clientId: z.string().min(1),
  tbId: z.string().min(1),
  templateId: z.string().min(1)
});

export type ContextInput = z.infer<typeof contextSchema>;
export type UploadInput = z.infer<typeof uploadSchema>;
export type MappingInput = z.infer<typeof mappingSchema>;
export type TemplateInput = z.infer<typeof templateSchema>;
export type DraftInput = z.infer<typeof draftSchema>;
