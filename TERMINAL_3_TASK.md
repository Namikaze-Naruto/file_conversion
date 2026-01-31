# 🧪 TERMINAL 3 - TESTING & BUG FIXES TASK

## Your Mission
Test all 100+ conversion types end-to-end and fix any bugs discovered.

## Copy This Prompt Into Terminal 3:
```
I have a file conversion platform with 100+ conversion types implemented across 10 categories.
The server is running at http://localhost:8000 with API docs at /docs.

I need you to:
1. Test all conversion endpoints systematically
2. Create test files for each format (or find/download sample files)
3. Fix any bugs or errors discovered
4. Document which conversions work and which need fixes

Categories to test:
1. Documents: PDF, DOCX, TXT, Excel, CSV (10+ conversions)
2. Images: JPG, PNG, WebP, SVG, HEIC, ICO (20+ conversions)
3. Audio: MP3, WAV, AAC, TTS, STT (15+ conversions)
4. Video: MP4, MKV, AVI, Video→GIF (10+ conversions)
5. Archives: ZIP, RAR, 7Z, TAR (8+ conversions)
6. Code: JSON, XML, YAML, CSV, HTML, Markdown (15+ conversions)
7. Design: PSD, SVG, DXF (5+ conversions)
8. Database: SQL, Parquet, Avro (6+ conversions)
9. Security: Base64, Hash, Encryption (8+ conversions)
10. AI: OCR, Image→Text (5+ conversions)

Testing approach:
- Start with document conversions (already known to work)
- Test image conversions next (high priority)
- Test audio/video (may need FFmpeg)
- Test code conversions (should work)
- Test archives, security, database
- Document any external dependencies needed (FFmpeg, Tesseract)

Create a test report showing:
- ✅ Working conversions
- ⚠️ Partially working (with notes)
- ❌ Not working (with error details)
- 📝 External tools needed

Fix critical bugs as you find them!
```

## What You'll Accomplish
- Comprehensive testing of all conversion endpoints
- Bug fixes for broken conversions
- Test file creation/gathering
- Detailed test report
- Identify missing dependencies

## Estimated Time
30-45 minutes

## Deliverables
- TEST_REPORT.md with all results
- Fixed any critical bugs
- Sample test files in test_files/ directory
- List of external dependencies needed

## Success Criteria
- All major conversion types tested
- Critical bugs fixed
- Clear documentation of what works
- Known issues documented

---

**Ready? Open a new terminal and run:**
```bash
gh copilot
# Then paste the prompt above
```
