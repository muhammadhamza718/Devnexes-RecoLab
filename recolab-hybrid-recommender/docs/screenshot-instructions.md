# Week 2 Submission Evidence Guide

## Required Submission Evidence

Per Devnexes weekly submission format, you must provide the following evidence for Week 2:

### 1. GitHub Repository Link
- Repository: https://github.com/muhammadhamza718/Devnexes-RecoLab
- Branch: `feature/week-2-implementation-content-model`
- Latest Commit: Commit hash and message

### 2. Screenshots/Screen Recording Required

You need visual evidence demonstrating the implemented functionality. Here's how to create each:

## Screenshot Instructions

### Option 1: Windows Snipping Tool (Built-in)
1. Press `Windows Key + Shift + S` to open Snipping Tool
2. Choose "Rectangular Snip"
3. Select the area of your screen to capture
4. The screenshot is automatically copied to clipboard
5. Press `Ctrl + S` to save the screenshot
6. Save as: `week-2-content-model-demo.png`

### Option 2: Windows Game Bar (Built-in)
1. Press `Windows Key + G` to open Game Bar
2. Click the camera icon to take a screenshot
3. Screenshots are saved in: `C:\Users\YourUsername\Videos\Captures`
4. Rename to: `week-2-content-model-demo.png`

### Option 3: PowerShell (Command Line)
```powershell
# Take screenshot of current window
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $bounds.width, $bounds.height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($bounds.Location, [System.Drawing.Drawing.Point]::Empty, $bounds.size)
$bitmap.Save("$HOME\Desktop\screenshot.png", [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
```

## Required Screenshots for Week 2

### Screenshot 1: Manual Test Results
**What to capture:**
- Run `python manual_tests.py` in the terminal
- Capture the terminal output showing all 5 tests passing
- Include the performance metrics (latency results)

**Terminal Command:**
```bash
cd F:\Courses\Hamza\Devnexes-Internship-Projects\recolab-hybrid-recommender
.\venv\Scripts\python.exe manual_tests.py
```

**Expected Output to Capture:**
```
MANUAL TESTING SUITE FOR WEEK 2 CONTENTMODEL
============================================================
TEST 1: Interactive ContentModel Testing
[PASS] Test 1 passed
TEST 2: Protocol Conformance Check
[PASS] Test 2 passed
TEST 3: Persistence Roundtrip Test
[PASS] Test 3 passed
TEST 4: Performance Test
Recommendation latency: 0.0034s
[PASS] Test 4 passed
TEST 5: Edge Case Testing
[PASS] Test 5 passed
TEST SUMMARY
Passed: 5/5
[SUCCESS] All manual tests passed!
```

### Screenshot 2: Automated Test Results
**What to capture:**
- Run automated pytest with coverage
- Show test results and coverage percentage

**Terminal Command:**
```bash
pytest -m "not full_dataset" --cov=src/recolab --cov-report=term
```

**Expected Output to Capture:**
```
============================= test session starts =============================
73 passed, 1 skipped, 2 deselected
=============================== coverage ================================
Name                         Stmts   Miss  Cover   Missing
----------------------------------------------------------
src\recolab\content.py         152     12    92%
TOTAL                          441     72    84%
```

### Screenshot 3: Code Quality Checks
**What to capture:**
- Run ruff linting and mypy type checking
- Show both checks passing

**Terminal Commands:**
```bash
ruff check src/
mypy src/
```

**Expected Output to Capture:**
```
All checks passed!
Success: no issues found in 7 source files
```

### Screenshot 4: Code Implementation
**What to capture:**
- Open `src/recolab/content.py` in your IDE
- Show the ContentModel class with key methods
- Include the protocol conformance (@runtime_checkable decorators)

**Key Code to Display:**
```python
@runtime_checkable
class Recommender(Protocol):
    def fit(self, ratings: pd.DataFrame, movies: pd.DataFrame | None = None) -> Recommender: ...
    def recommend(self, user_id: int, k: int, exclude_items: set[int] | None = None) -> list[int]: ...

@dataclass
class ContentModel(Recommender, ColdStartHandler):
    """Content-based recommender using TF-IDF + cosine similarity"""
```

## Screen Recording Instructions (Optional but Recommended)

### Option 1: OBS Studio (Free, Professional)
1. Download OBS Studio from https://obsproject.com/
2. Install and launch OBS Studio
3. Click "+" → "Display Capture" to record your screen
4. Set recording quality: 1920x1080, 30fps
5. Click "Start Recording"
6. Run the manual tests: `python manual_tests.py`
7. Click "Stop Recording"
8. Save as: `week-2-content-model-demo.mp4`

### Option 2: Windows Game Bar (Built-in)
1. Press `Windows Key + G` to open Game Bar
2. Click the record button (circle)
3. Run the manual tests in terminal
4. Press `Windows Key + G` again to stop recording
5. Video saved in: `C:\Users\YourUsername\Videos\Captures`

### Option 3: Loom (Free, Cloud-based)
1. Download Loom from https://www.loom.com/
2. Install and sign in
3. Click "New Recording" → "Screen Only"
4. Run the manual tests
5. Stop recording
6. Loom provides a shareable link

## Screen Recording Script for Week 2

Use this script to demonstrate key functionality:

```bash
# Week 2 Content Model Demo Script

# 1. Show project structure
dir
cd src/recolab
dir

# 2. Show test results
cd ..\..
pytest -m "not full_dataset" -v

# 3. Show manual tests
python manual_tests.py

# 4. Show code quality
ruff check src/
mypy src/

# 5. Show coverage report
pytest --cov=src/recolab --cov-report=html
# Open htmlcov/index.html in browser

# 6. Show documentation
type README.md
type docs\week-2-learning-notes.md
```

## Where to Place Screenshots

1. **Screenshots**: Place in `recolab-hybrid-recommender/docs/screenshots/`
2. **Screen Recordings**: Place in `recolab-hybrid-recommender/docs/videos/`
3. **README Reference**: Add screenshot section to README.md

## README Screenshot Section Template

Add this section to your README.md:

```markdown
## Screenshots and Demo

### Week 2: Content-Based Recommendation Model

#### Manual Test Results
![Manual Tests](docs/screenshots/week-2-manual-tests.png)

#### Automated Test Coverage
![Test Coverage](docs/screenshots/week-2-coverage.png)

#### Code Quality Checks
![Code Quality](docs/screenshots/week-2-code-quality.png)

#### Implementation
![ContentModel Code](docs/screenshots/week-2-implementation.png)

### Screen Recording
[Watch Week 2 Demo](docs/videos/week-2-content-model-demo.mp4)
```

## Weekly Progress Note Template

```markdown
## Week 2 Progress Note

### Completed Work
- ✅ Content-based recommendation model implementation
- ✅ TF-IDF feature extraction and cosine similarity
- ✅ Cold-start handling with genre-based filtering
- ✅ Protocol-oriented design (Recommender, ColdStartHandler)
- ✅ Comprehensive testing (34 tests, 92% coverage)
- ✅ CI-safe test fixtures
- ✅ Documentation (README, learning notes, technical acquisition record)

### Pending Work
- ⏳ Week 3: Collaborative filtering model
- ⏳ Week 4: Hybrid model integration
- ⏳ Week 5: UI development (FastAPI + Next.js)
- ⏳ Week 6: Deployment and evaluation

### Blockers
- None

### Decisions
- Chose TF-IDF over Word2Vec for simplicity and interpretability
- Used protocol-oriented design for flexibility
- Implemented CI-safe fixtures for fast automated testing
- Configured mypy to ignore scikit-learn (no official stubs)

### Next Week Tasks
1. Implement collaborative filtering model (user-based, item-based)
2. Define model comparison framework
3. Add performance benchmarks
4. Begin hybrid model planning
```

## Final Checklist

Before submitting Week 2 evidence:

- [ ] Screenshots taken (4 required screenshots)
- [ ] Screenshots saved in `docs/screenshots/`
- [ ] Screen recording created (optional but recommended)
- [ ] README.md updated with screenshot section
- [ ] Weekly progress note written
- [ ] GitHub repository link ready
- [ ] Latest commit hash identified
- [ ] Screenshots demonstrate working functionality
- [ ] All quality checks visible in screenshots
- [ ] Evidence clearly labeled and organized

## Submission Format

Combine all evidence into a single message:

```
**Week 2 Submission Evidence**

**GitHub Repository**: https://github.com/muhammadhamza718/Devnexes-RecoLab
**Branch**: feature/week-2-implementation-content-model
**Latest Commit**: c8ee0fa (Fix manual testing script import error)

**Weekly Progress Note**: [Paste your progress note here]

**Screenshots**: [Attach 4 screenshots]
- Manual test results
- Automated test coverage
- Code quality checks
- Implementation code

**Screen Recording**: [Attach or provide link if created]

**Next Week Tasks**: [List Week 3 tasks]
```

## Tips for Better Screenshots

1. **Clear Terminal**: Increase terminal font size for readability
2. **Window Arrangement**: Arrange windows to show multiple test results
3. **Highlight Success**: Use green checkmarks or success indicators
4. **Include Context**: Show file paths and commands used
5. **High Resolution**: Capture at 1920x1080 or higher
6. **Consistent Naming**: Use descriptive filenames
7. **File Format**: Use PNG for screenshots, MP4 for videos