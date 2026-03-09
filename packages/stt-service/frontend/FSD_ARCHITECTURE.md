# Feature-Sliced Design (FSD) Architecture

## Overview

This project follows **Feature-Sliced Design (FSD)** methodology for a clean, scalable architecture.

## Structure

```
src/
├── entities/          # Business entities (reusable across features)
│   └── speaker/       # Speaker entity for diarization
│       ├── ui/        # UI components
│       │   ├── SpeakerBlock.tsx      (22 lines) ✅
│       │   ├── SpeakerBlock.css
│       │   ├── SpeakerLegend.tsx     (32 lines) ✅
│       │   └── SpeakerLegend.css
│       ├── lib/       # Business logic & utilities
│       │   └── formatSpeakers.ts     (60 lines) ✅
│       └── index.ts   # Public API
│
├── features/          # User-facing features
│   ├── transcription/ # Transcription result display
│   │   ├── ui/
│   │   │   ├── TranscriptionResult.tsx  (91 lines) ✅
│   │   │   └── TranscriptionResult.css
│   │   └── index.ts   # Public API
│   └── upload/        # File upload feature
│
└── shared/            # Shared utilities & types
    ├── ui/            # Common UI components
    ├── lib/           # Helper functions
    └── types/         # TypeScript types
```

## Clean Code Rules

### File Size Limits ✅
- **Max 200 lines** per file
- **Max 150 lines** for entity components
- **Max 100 lines** for simple components

### Single Responsibility Principle
- Each file has **one clear purpose**
- Logic extracted into utilities
- Components focus on presentation

### Ultra-Compact Spacing ⚠️
**CRITICAL:** SpeakerBlock uses **NO WHITESPACE** in HTML template:
```tsx
<div className={`speaker-block speaker-${speakerNum}`}><div className="speaker-avatar">S{displayNum}</div><div className="speaker-content">...</div></div>
```

This maintains ultra-compact visual spacing:
- Avatar: 28px (desktop), 24px (mobile)
- Gap: 4px between avatar and content
- Padding: 2px 8px in bubble
- Line-height: 1.2
- Margin: 1px between blocks

## Imports

### Public API (Recommended)
```tsx
// From entities
import { SpeakerBlock, SpeakerLegend, aggregateSpeakerText } from 'entities/speaker';

// From features
import { TranscriptionResult } from 'features/transcription';
```

### Direct Imports (Avoid)
```tsx
// Don't do this (breaks encapsulation)
import SpeakerBlock from 'entities/speaker/ui/SpeakerBlock';
```

## Benefits

1. **Scalability** - Clear boundaries between layers
2. **Maintainability** - Easy to find and modify code
3. **Reusability** - Entities can be used across features
4. **Testability** - Logic separated from UI
5. **Code Quality** - File size limits enforce clean code

## Migration Guide

Old structure:
```
src/components/SpeakerBlock.tsx
src/utils/textFormatting.ts
```

New structure:
```
src/entities/speaker/ui/SpeakerBlock.tsx
src/entities/speaker/lib/formatSpeakers.ts
```

Update imports:
```tsx
// Before
import { aggregateSpeakerText } from '../utils/textFormatting';

// After
import { aggregateSpeakerText } from 'entities/speaker';
```

## References

- [Feature-Sliced Design](https://feature-sliced.design/)
- [Clean Code by Robert C. Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
