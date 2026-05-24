# Curriculum Question Extractor

Legacy notes from the earlier draft are archived in `notes.md`.

## Project Overview
A Streamlit app for turning OCR/PDF text into validated curriculum-question JSON, saving it as datasets, and browsing those datasets later.

## Tech Stack
- Python
- Streamlit
- pandas
- JSON file storage
- Local filesystem registry

## Architecture Overview
- `app.py`: main extraction and dataset-registry UI
- `pages/01_Student.py`: student/lesson dashboard
- `pages/02_Question.py`: single-dataset explorer
- `pages/03_Question_Combined.py`: combined dataset explorer
- `utils/prompt_loader.py`: loads prompt text from `prompts/`
- `utils/json_validator.py`: checks output schema
- `utils/storage.py`: saves datasets and registry entries
- `utils/lesson_registry.py`: lesson/student registry
- `data/`: saved JSON datasets and registries

## Installation & Setup
1. Create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage Guide
1. Pick a prompt from the sidebar.
2. Paste OCR or PDF text.
3. Paste model JSON output.
4. Click `Validate`.
5. Preview or save the dataset.
6. Browse saved datasets in the registry table.
7. Open the Streamlit pages for student and question views.

## API Reference
No external HTTP API. Internal helpers:
- `save_dataset(data)`
- `load_registry()`
- `load_dataset(filename)`
- `validate_schema(data)`

## Environment Variables
None required.

## Contributing Guide
- Keep JSON schemas stable.
- Add new prompts under `prompts/`.
- Update validators before changing the saved question shape.
- Run `python3 -m py_compile ...` before opening a PR.

## License
No license file is present yet.

## Scaling Guide
### Current Bottlenecks
- Flat JSON files will be the first bottleneck.
- Local disk writes will not scale cleanly.
- Streamlit is single-app, synchronous UI logic.
- Large registries will become slow to filter in-memory.

### Database Scaling
- Move `registry.json` to PostgreSQL.
- Add indexes on `topic`, `filename`, `created_at`, and lesson/student IDs.
- Cache hot registry queries in Redis.
- Use read replicas for heavy browse traffic.
- Shard only after a real multi-tenant or very large dataset need.

### Backend Scaling
- Keep Streamlit for the UI, but move ingestion to an API worker.
- Use horizontal scaling behind a load balancer.
- Prefer stateless workers over vertical-only scaling.
- Offload validation and file writes to a queue.

### Frontend Scaling
- Put static assets behind a CDN.
- Lazy-load large dataset views.
- Consider SSR/SSG only if you rebuild the UI outside Streamlit.
- Paginate tables early.

### Infrastructure
- AWS: CloudFront, S3, ECS Fargate or App Runner, RDS Postgres, ElastiCache Redis, ALB, CloudWatch.
- GCP: Cloud Run, Cloud SQL, Cloud Storage, Cloud CDN, Memorystore.
- Azure: Container Apps or App Service, Azure Database for PostgreSQL, Blob Storage, Front Door, Azure Cache for Redis.

### Cost Estimate
Excluding LLM/API usage:
- 1k users: about $50 to $200/month
- 10k users: about $300 to $1,000/month
- 100k users: about $1,500 to $8,000/month

### Roadmap
1. Replace JSON registry with PostgreSQL.
2. Move dataset files to object storage.
3. Add background jobs for validation and ingestion.
4. Add auth, roles, and audit logs.
5. Add caching and CDN.
6. Split browse and write paths.
7. Add observability and autoscaling.
8. Add search, analytics, and exports.

## Similar Apps / Companies
| Product | What it does | Tech stack | Business model | Scale | Why it wins |
|---|---|---|---|---|---|
| Quizlet | Flashcards, practice, study sets | Not publicly disclosed | Freemium + paid plans | Large consumer scale | Huge UGC library and simple study loops |
| Kahoot! | Live quizzes and learning games | Not publicly disclosed | Freemium + premium plans | Global, billions of participants | Viral game loop and broad use cases |
| Quizizz | Interactive quizzes, lessons, AI creation | Not publicly disclosed | Freemium + school/enterprise plans | Large K-12 adoption | Easy authoring and classroom pacing |
| IXL | Adaptive practice and curriculum drills | Not publicly disclosed | Subscription | 18M+ students | Strong personalization and analytics |
| Nearpod | Interactive lessons and formative checks | Not publicly disclosed | Freemium + school/district licensing | Used across many U.S. districts | Teacher workflow + district sales |
| Edpuzzle | Video lessons with embedded questions | Not publicly disclosed | Freemium + paid school plans | Millions of teachers | Simple video-to-assessment workflow |
| Socrative | Quizzes, polls, exit tickets | Not publicly disclosed | Freemium + Pro/enterprise | Millions of users | Fast, low-friction formative checks |
| Formative | Real-time assessment and feedback | Not publicly disclosed | Freemium + paid school/district plans | Large district adoption | Immediate feedback and AI features |
| Blooket | Game-based classroom practice | Not publicly disclosed | Freemium + Plus | Millions of educators | Fun game mechanics and social virality |
| Quizalize | Quiz creation and classroom practice | Not publicly disclosed | Free + premium plans | 250k+ teachers, global reach | Clear teacher value and international reach |

## What Makes Them Successful
- They reduce teacher setup time.
- They keep the student experience lightweight.
- They use freemium to drive adoption.
- They support classroom workflows, not just content.
- They benefit from network effects and reusable content.

## Project Niche
- Curriculum-specific question extraction from OCR/PDF text.
- Structured JSON output with validation.
- Local-first dataset registry.
- Lesson-aware student mapping.
- Better fit for internal teaching ops than generic quiz tools.
