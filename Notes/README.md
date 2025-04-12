# README

As a technical manager, you handle information from various sources like team meetings, one-on-ones, and strategic planning sessions. Without a good system, valuable insights can be lost.

This guide presents a lightweight note-taking system that:
- Applies principles from the Zettelkasten method to create a network of interconnected knowledge
- Uses a structured file organization to keep notes accessible and maintainable
- Utilizes VS Code with Markdown files for version control and sharing
- Grows organically with minimal upfront setup

## Introducing Brewtiful

To illustrate these concepts, we'll use a fictional company, **Brewtiful**, which specializes in a Smart Coffee Machine that integrates mood analysis, customer preferences, and enterprise systems to provide a personalized and efficient coffee brewing experience. This machine uses advanced technologies like voice and facial recognition to understand customer moods and tailor coffee types accordingly. The notes from Brewtiful's technical manager will serve as examples throughout this guide.

All example notes for Brewtiful can be found in this directory. These notes were created with the assistance of large language models including Gemini 2.0, GPT 4.5, and Claude 3.7 Sonnet to demonstrate effective note-taking practices for technical managers.

## Zettelkasten Principles and Folder Structure

The Zettelkasten method emphasizes creating a network of interconnected ideas that evolves organically. At Brewtiful, this approach is combined with a clear folder structure to organize notes effectively while maintaining flexibility.

### Key Principles of Zettelkasten

1. **Atomic Notes**: Each note should focus on a single idea or concept.
2. **Interconnectedness**: Notes are linked using wiki-style links (e.g., `[[Facial Recognition API]]`), forming a web of related ideas.
3. **Tagging and Metadata**: Each note includes YAML front matter with metadata (e.g., tags) to make it easier to categorize and search for notes.
4. **Discoverability**: Notes are organized into folders based on their domain, with each folder containing an index file called `_springboard.md` that provides an overview and links to key notes.

### Folder Structure at Brewtiful

The folder structure reflects the different domains of responsibility for a technical manager:

- **Journal/**: Contains daily notes summarizing meetings such as standups, product alignments or retrospectives.
- **Leadership/**: Covers leadership concepts (e.g. T-shaped upskilling) and HR policies (e.g. onboarding).
- **People/**: Stores notes from 1:1 meetings with team members and your manager.
- **Product/**: Contains notes on the business case, product backlog items, and roadmap planning.
- **TechnicalNotes/**: Includes high-level design documents and API specifications.

### Springboard Files

Each folder includes a `_springboard.md` file that acts as an index for that domain:
- Provides an overview of the subject area
- Links to all relevant notes within the folder
- Helps maintain context when navigating between domains

#### Example: `_springboard_technical.md`

```markdown
---
title: springboard_technical
date: 2025-01-03
categories:
  - Technical 
tags:
  - Springboard
  - High-Level-Design
  - API
  - Specification
---

## Overview

This note serves as a springboard for exploring topics related to technical aspects of the Brewtiful ecosystem.
It is split into the following main categories:

### 1. High-level design

The [[high_level_design]] contains information on system architecture, component interactions, and overall system design.

### 2. API Specification

The [[api_spec]] contains information on naming conventions, security, error handling, versioning, data validation, and API definitions.

**Tags**: #HighLevelDesign #API #Specification
```

## Markdown Primer

Markdown is a lightweight markup language that allows you to format text using plain syntax. Documents can be created in any code editor; most users will be familiar with VS Code, where you can write notes in Markdown syntax while previewing them side-by-side using the built-in preview feature (`Ctrl + K V`) or opening it in a separate tab (`Ctrl + Shift + V`).

### Basic Syntax

1. **Headers**: Use `#` for headings (`#` for H1, `##` for H2, etc.).
2. **Bold/Italic**: Use `**bold**` or `*italic*` for emphasis.
3. **Lists**: Create unordered lists with `-` or ordered lists with numbers (`1.`).
4. **Code Blocks**: Wrap code in triple backticks (\`\`\`) for syntax highlighting.

### Special Features for Note-Taking

1. **Front Matter**  
   Add metadata at the top of each note using YAML front matter. For example:
   ```yaml
   ---
   title: springboard_technical
   date: 2025-01-03
   categories:
     - Technical 
   tags:
     - Springboard
     - High-Level-Design
     - API
     - Specification
   ---
   ```

2. **Tags**  
   Tags are useful for categorizing notes by topic or theme. You can include them in the YAML front matter or inline using hashtags:
   - Example in YAML front matter: `tags: [Springboard, High-Level-Design]`
   - Example inline: `#Springboard #API`

3. **Wiki Links**  
   Use double brackets (`[[ ]]`) to link one note to another within your system:
   - Example: `[[Facial Recognition API]]` links to the note titled "Facial Recognition API."
   These links make it easy to navigate between related ideas and build a network of interconnected knowledge.

4. **To-do Lists**  
   Use `- [ ]` for tasks and `- [x]` for completed tasks:
   ```markdown
   - [ ] Implement mood analysis algorithm
   - [x] Finalize high-level design document
   ```

5. **Mermaid Diagrams**  
   Mermaid allows you to create diagrams directly in Markdown using simple text-based syntax. For example:

   ```mermaid
   
   graph TD;
   A-->B;
   A-->C;
   B-->D;
   C-->D;
   
   ```
   
   This produces flowcharts, sequence diagrams, Gantt charts, and more dynamically rendered alongside your text.

6. **Foam Integration**  
   Foam is an extension you can add to VS Code that enhances your Markdown-based note-taking workflow:
   - Visualizes connections between your notes via an interactive graph.
   - Automatically updates links when files are renamed.
   - Provides backlinking functionality to see references between notes.
   - Supports templates for consistent formatting across different types of notes.

