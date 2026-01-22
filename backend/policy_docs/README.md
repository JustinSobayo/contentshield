# Policy Documents

This folder contains policy documents for different platforms.

## Supported Platforms:
- YouTube Community Guidelines
- TikTok Community Guidelines  
- Instagram Community Guidelines
- Twitter Community Guidelines

## File Format:
- PDF files are supported
- Documents should be named with platform name (e.g., Youtube:`support.google.com-policy.pdf`, Twitter(X)`.(X)Twitter.pdf`, Tiktok:`.TikTok.pdf`, Instagram:`.Instagram.pdf`)
- Documents will be automatically indexed when the server starts

## Adding New Documents:
1. Place PDF files in this directory
2. Restart the server or call `/index-documents` endpoint
3. Documents will be automatically processed and indexed

## Document Processing:
- Documents are chunked into smaller segments
- Vector embeddings are generated using Gemini embeddings
- Documents are stored in Chroma vector database
- Metadata includes platform information for filtering
