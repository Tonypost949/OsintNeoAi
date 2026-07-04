/**
 * Entity extraction utilities for OSINT analysis
 * Extracts people names, emails, and phone numbers from text
 */

export interface ExtractedEntity {
  name: string;
  normalizedName: string;
  type: "person" | "email" | "phone";
}

export interface ExtractionResult {
  people: ExtractedEntity[];
  emails: ExtractedEntity[];
  phones: ExtractedEntity[];
  allEntities: ExtractedEntity[];
}

// Regex patterns for entity extraction
const EMAIL_PATTERN = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g;
const PHONE_PATTERN = /\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g;
const NAME_PATTERN = /\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b/g;

/**
 * Normalize text for comparison (lowercase, trim, remove extra spaces)
 */
export function normalizeText(text: string): string {
  return text.toLowerCase().trim().replace(/\s+/g, " ");
}

/**
 * Extract emails from text
 */
export function extractEmails(text: string): ExtractedEntity[] {
  const matches = text.match(EMAIL_PATTERN) || [];
  const seen = new Set<string>();
  
  return Array.from(matches)
    .filter(email => {
      const normalized = normalizeText(email);
      if (seen.has(normalized)) return false;
      seen.add(normalized);
      return true;
    })
    .map(email => ({
      name: email,
      normalizedName: normalizeText(email),
      type: "email" as const,
    }));
}

/**
 * Extract phone numbers from text
 */
export function extractPhones(text: string): ExtractedEntity[] {
  const matches = text.match(PHONE_PATTERN) || [];
  const seen = new Set<string>();
  
  return Array.from(matches)
    .filter(phone => {
      // Normalize phone by removing non-digits
      const digits = phone.replace(/\D/g, "");
      if (seen.has(digits)) return false;
      seen.add(digits);
      return true;
    })
    .map(phone => ({
      name: phone,
      normalizedName: phone.replace(/\D/g, ""), // Store only digits for normalization
      type: "phone" as const,
    }));
}

/**
 * Extract person names from text using regex patterns
 * This is a basic implementation - for better results, integrate spaCy NLP
 */
export function extractPeople(text: string): ExtractedEntity[] {
  const matches = text.match(NAME_PATTERN) || [];
  const seen = new Set<string>();
  
  return Array.from(matches)
    .filter(name => {
      // Filter out common non-person words
      const lowerName = name.toLowerCase();
      const commonWords = ["the", "and", "for", "with", "from", "about", "which", "their", "would", "could", "should"];
      if (commonWords.includes(lowerName)) return false;
      
      // Require at least 2 words (first and last name)
      if (name.split(/\s+/).length < 2) return false;
      
      const normalized = normalizeText(name);
      if (seen.has(normalized)) return false;
      seen.add(normalized);
      return true;
    })
    .map(name => ({
      name,
      normalizedName: normalizeText(name),
      type: "person" as const,
    }));
}

/**
 * Extract all entities from text
 */
export function extractEntities(text: string): ExtractionResult {
  const people = extractPeople(text);
  const emails = extractEmails(text);
  const phones = extractPhones(text);
  
  // Combine all entities
  const allEntities = [...people, ...emails, ...phones];
  
  return {
    people,
    emails,
    phones,
    allEntities,
  };
}

/**
 * Find co-occurrences of entities in text
 * Returns pairs of entities that appear together
 */
export function findCoOccurrences(entities: ExtractedEntity[]): Array<[ExtractedEntity, ExtractedEntity]> {
  const pairs: Array<[ExtractedEntity, ExtractedEntity]> = [];
  
  // For each pair of entities, check if they appear in the same text
  for (let i = 0; i < entities.length; i++) {
    for (let j = i + 1; j < entities.length; j++) {
      pairs.push([entities[i], entities[j]]);
    }
  }
  
  return pairs;
}

/**
 * Extract entities from different file types
 */
export async function extractFromText(text: string): Promise<ExtractionResult> {
  return extractEntities(text);
}

export async function extractFromPDF(buffer: Buffer): Promise<ExtractionResult> {
  try {
    const pdfParse = require('pdf-parse');
    const data = await pdfParse(buffer);
    const text = data.text || "";
    return extractEntities(text);
  } catch (error) {
    console.error("PDF parsing error:", error);
    return {
      people: [],
      emails: [],
      phones: [],
      allEntities: [],
    };
  }
}

export async function extractFromDOCX(buffer: Buffer): Promise<ExtractionResult> {
  try {
    const { Document } = require('docx');
    const doc = await Document.load(buffer);
    
    let text = "";
    if (doc.sections) {
      for (const section of doc.sections) {
        if (section.children) {
          for (const child of section.children) {
            if (child.text) {
              text += child.text + " ";
            } else if (child.children) {
              for (const subChild of child.children) {
                if (subChild.text) {
                  text += subChild.text + " ";
                }
              }
            }
          }
        }
      }
    }
    
    return extractEntities(text);
  } catch (error) {
    console.error("DOCX parsing error:", error);
    return {
      people: [],
      emails: [],
      phones: [],
      allEntities: [],
    };
  }
}

export async function extractFromCSV(text: string): Promise<ExtractionResult> {
  // Parse CSV and extract entities from all cells
  const lines = text.split("\n");
  const allText = lines.join(" ");
  return extractEntities(allText);
}

export async function extractFromJSON(text: string): Promise<ExtractionResult> {
  try {
    const data = JSON.parse(text);
    const allText = JSON.stringify(data);
    return extractEntities(allText);
  } catch {
    return {
      people: [],
      emails: [],
      phones: [],
      allEntities: [],
    };
  }
}

export async function extractFromEML(text: string): Promise<ExtractionResult> {
  // Parse email headers and body
  // Extract from From, To, Subject, and body
  return extractEntities(text);
}

/**
 * Route extraction based on file type
 */
export async function extractByFileType(fileType: string, content: string | Buffer): Promise<ExtractionResult> {
  const type = fileType.toLowerCase();
  
  if (typeof content === "string") {
    if (type === "txt") return extractFromText(content);
    if (type === "csv") return extractFromCSV(content);
    if (type === "json") return extractFromJSON(content);
    if (type === "eml") return extractFromEML(content);
  } else {
    if (type === "pdf") return extractFromPDF(content);
    if (type === "docx") return extractFromDOCX(content);
  }
  
  return {
    people: [],
    emails: [],
    phones: [],
    allEntities: [],
  };
}
