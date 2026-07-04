# OSINT Analyzer - Project TODO

## Database & Core Infrastructure
- [x] Define database schema (analyses, entities, relationships, files)
- [x] Create entity extraction utilities (regex patterns, NLP integration)
- [ ] Implement file parsing for TXT, PDF, DOCX, CSV, JSON, EML
- [x] Build relationship mapping and co-occurrence calculation

## File Upload & Processing
- [x] Create file upload UI with drag-and-drop support
- [x] Implement file upload handler and validation
- [x] Build file processing pipeline with progress tracking
- [x] Add support for multiple file formats

## Analysis & Entity Extraction
- [x] Implement person name extraction (regex + NLP fallback)
- [x] Extract email addresses and phone numbers
- [x] Build entity deduplication and normalization
- [x] Create analysis result storage

## Visualization & Reports
- [x] Build D3.js interactive network graph component
- [x] Implement node sizing by file appearances
- [x] Implement edge weighting by co-occurrence count
- [x] Create text report generation
- [x] Implement CSV export for people and relationships

## PDF/DOCX Parsing
- [x] Install pdf-parse and docx libraries
- [x] Implement PDF text extraction
- [x] Implement DOCX text extraction
- [x] Update file processing pipeline to use new parsers

## Google Drive Integration
- [x] Set up Google Drive OAuth authentication
- [x] Build Drive file scanner and downloader
- [x] Integrate Drive files into analysis pipeline
- [x] Create Drive account management UI

## Advanced Filtering
- [x] Implement entity type filtering (person, email, phone)
- [x] Add connection strength filtering
- [x] Add file count range filtering
- [x] Create search functionality

## Dashboard & Results Management
- [x] Create analysis dashboard with statistics
- [x] Implement results filtering and search
- [ ] Add results export functionality
- [ ] Build results comparison view

## UI & Polish
- [ ] Design clean, functional layout
- [ ] Build navigation and routing
- [ ] Implement loading states and error handling
- [ ] Add responsive design for mobile
- [ ] Polish interactions and micro-animations

## Testing & Deployment
- [ ] Write unit tests for entity extraction
- [ ] Test file upload and processing pipeline
- [ ] Test visualization with sample data
- [ ] Performance optimization
- [ ] Final QA and bug fixes
