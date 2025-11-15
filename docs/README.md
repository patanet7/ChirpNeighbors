# ChirpNeighbors Documentation

Complete documentation for the ChirpNeighbors IoT bird sound monitoring system.

## Documentation Structure

### 📋 [agents/](./agents/)
AI agent task logs tracking automated work performed on the project.
- **Format**: `YYYYMMDD_HHMMSS_task-description.md`
- **Purpose**: Transparency, history, and context for future development
- **View**: [Agent logs README](./agents/README.md)

### 🏗️ [architecture/](./architecture/)
System design and architecture documentation.
- High-level system overview
- Component interaction diagrams
- Data flow and processing pipeline
- Deployment architecture
- Scalability considerations
- [Product Requirements Document](./architecture/product-requirements.md)

### 🔧 [hardware/](./hardware/)
Hardware specifications and design documents.
- ESP32 pinout and configuration
- Digital microphone specifications
- PCB schematics (if custom board)
- Bill of Materials (BOM)
- Power consumption analysis
- Assembly instructions

### 📡 [api/](./api/)
Backend API documentation.
- REST API endpoints
- Request/response schemas
- Authentication and authorization
- WebSocket specifications (if applicable)
- Error codes and handling
- API versioning strategy

## Quick Links

- **Project Context**: [claude.md](../claude.md) - AI assistant context file
- **Main README**: [README.md](../README.md) - Project overview
- **Source Code**: See `/firmware/`, `/backend/`, `/frontend/` (when created)

## Contributing to Documentation

### Adding New Documentation

1. **Choose the right location**:
   - Architecture design → `architecture/`
   - Hardware specs → `hardware/`
   - API changes → `api/`
   - Agent work → `agents/` (auto-generated)

2. **Use Markdown** (`.md` files)

3. **Include diagrams** where helpful (Mermaid, SVG, or PNG)

4. **Keep it current**: Update docs when code changes

### Documentation Standards

- **Format**: GitHub-flavored Markdown
- **Diagrams**: Mermaid for flowcharts/sequence diagrams
- **Code Examples**: Include language tags for syntax highlighting
- **Links**: Use relative paths for internal links
- **Images**: Store in `docs/images/` subdirectory

### Example Documentation Template

```markdown
# Feature/Component Name

## Overview
Brief description of what this documents

## Details
Comprehensive explanation with:
- Technical specifications
- Implementation notes
- Usage examples
- Configuration options

## Examples

\`\`\`python
# Code example
\`\`\`

## Related Documentation
- [Link to related doc](./related-doc.md)
```

## Building Documentation Site (Future)

When the project grows, consider setting up:
- **Docusaurus** or **MkDocs** for static site generation
- **Automated deployment** to GitHub Pages or Vercel
- **Search functionality** for easy navigation
- **Versioning** for different releases

## Questions?

For documentation questions or suggestions:
1. Check existing docs first
2. Review [claude.md](../claude.md) for project context
3. Open a GitHub issue with the `documentation` label
