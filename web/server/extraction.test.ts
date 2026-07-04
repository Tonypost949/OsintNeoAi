import { describe, it, expect } from "vitest";
import { extractEntities, extractEmails, extractPhones, extractPeople, normalizeText, findCoOccurrences } from "./extraction";

describe("Entity Extraction", () => {
  describe("normalizeText", () => {
    it("should normalize text to lowercase and trim", () => {
      expect(normalizeText("  HELLO WORLD  ")).toBe("hello world");
    });

    it("should remove extra spaces", () => {
      expect(normalizeText("hello    world")).toBe("hello world");
    });
  });

  describe("extractEmails", () => {
    it("should extract email addresses", () => {
      const text = "Contact john.doe@example.com or jane_smith@company.org";
      const emails = extractEmails(text);
      
      expect(emails).toHaveLength(2);
      expect(emails[0].name).toBe("john.doe@example.com");
      expect(emails[0].type).toBe("email");
      expect(emails[1].name).toBe("jane_smith@company.org");
    });

    it("should deduplicate emails", () => {
      const text = "Email: test@example.com and test@example.com again";
      const emails = extractEmails(text);
      
      expect(emails).toHaveLength(1);
    });

    it("should return empty array for text without emails", () => {
      const text = "No emails here";
      const emails = extractEmails(text);
      
      expect(emails).toHaveLength(0);
    });
  });

  describe("extractPhones", () => {
    it("should extract phone numbers", () => {
      const text = "Call (555) 123-4567 or +1-555-987-6543";
      const phones = extractPhones(text);
      
      expect(phones.length).toBeGreaterThan(0);
      expect(phones[0].type).toBe("phone");
    });

    it("should deduplicate phones", () => {
      const text = "Phone: 555-123-4567 and 555-123-4567";
      const phones = extractPhones(text);
      
      expect(phones).toHaveLength(1);
    });
  });

  describe("extractPeople", () => {
    it("should extract person names", () => {
      const text = "John Smith and Jane Doe met with Bob Johnson";
      const people = extractPeople(text);
      
      expect(people.length).toBeGreaterThan(0);
      expect(people.some(p => p.name.includes("John Smith"))).toBe(true);
    });

    it("should filter out single words", () => {
      const text = "The quick brown fox";
      const people = extractPeople(text);
      
      expect(people).toHaveLength(0);
    });

    it("should deduplicate names", () => {
      const text = "John Smith and John Smith again";
      const people = extractPeople(text);
      
      expect(people).toHaveLength(1);
    });
  });

  describe("extractEntities", () => {
    it("should extract all entity types", () => {
      const text = `
        John Smith (john@example.com, 555-123-4567) met with Jane Doe.
        Contact: bob@company.org or call (555) 987-6543
      `;
      const result = extractEntities(text);
      
      expect(result.people.length).toBeGreaterThan(0);
      expect(result.emails.length).toBeGreaterThan(0);
      expect(result.phones.length).toBeGreaterThan(0);
      expect(result.allEntities.length).toBeGreaterThan(0);
    });
  });

  describe("findCoOccurrences", () => {
    it("should find pairs of entities", () => {
      const entities = [
        { name: "John", normalizedName: "john", type: "person" as const },
        { name: "Jane", normalizedName: "jane", type: "person" as const },
        { name: "Bob", normalizedName: "bob", type: "person" as const },
      ];
      
      const pairs = findCoOccurrences(entities);
      
      expect(pairs).toHaveLength(3); // C(3,2) = 3
      expect(pairs[0][0].name).toBe("John");
      expect(pairs[0][1].name).toBe("Jane");
    });
  });
});
