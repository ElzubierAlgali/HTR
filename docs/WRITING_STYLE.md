# Writing Style (locked)

House style for every chapter source in `docs/` and every `scripts/rebuild_*_docx.py` builder.

## Voice

Impersonal third person throughout the thesis body, including the Abstract.

| Use | Avoid |
|-----|-------|
| this study, this thesis, the chapter, the evaluation | I, my, we, our |
| the study evaluates | I evaluate |
| the outcome is informative | I regard this outcome as informative |

The Arabic abstract follows the same rule: impersonal or passive verb forms rather than first-person conjugations.

## Humanization rules

1. **Vary sentence length.** Mix short declaratives of eight to twelve words with longer ones. Avoid a uniform rhythm of thirty-plus-word multi-clause sentences.
2. **Limit em-dashes** to at most one per section. Prefer commas, colons, or a full stop.
3. **Break up decorative parallel lists.** Long chains such as "data preparation, training, evaluation, logging, and demonstration" should be split across sentences or trimmed.
4. **Delete stock signposting and intensifiers.** Banned: "deliberately", "intentionally", "It is worth noting", "In keeping with conventional thesis organisation", "Equally important is what this chapter withholds", "It should be emphasised that".
5. **Prefer verbs to nominalizations.** "dataset characterisation" becomes "describes the dataset".
6. **No narrative or ornamental framing.** No story voice, no metaphor chains, no "our hero", no "digital alchemy".
7. **British -ise spelling**, matching the existing "normalisation", "optimisation", "specialised".

## Hard guardrail

A style pass changes wording only. It must never alter:

- any number, percentage, or sample count
- any `{{METRIC:run_id.field}}` token
- any table value, citation, or reference
- any claim about what was measured

## Scope of application

| File | Voice enforced |
|------|----------------|
| `docs/CHAPTER_1_INTRODUCTION.md` | yes |
| `docs/CHAPTER_2_LITERATURE_REVIEW.md` | yes |
| `docs/CHAPTER_3_METHODOLOGY.md` | yes (already compliant) |
| `docs/CHAPTER_4_IMPLEMENTATION_RESULTS.md` | yes |
| `docs/CHAPTER_5_CONCLUSION.md` | yes |
| `docs/ABSTRACT.md` | yes (English and Arabic) |

Chapter prose is duplicated between each markdown source and its `rebuild_*_docx.py` builder. Both copies must be edited together or the DOCX and markdown will diverge.
