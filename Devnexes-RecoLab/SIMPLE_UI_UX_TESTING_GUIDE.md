# Simple Streamlit UI/UX Testing Guide

**Quick Step-by-Step Testing Instructions**

---

## Setup (Do this first)

**Step 1: Start the Application**
```bash
cd F:\Courses\Hamza\Devnexes-Internship-Projects\Devnexes-RecoLab
python -m streamlit run streamlit_app.py
```

**Step 2: Open Browser**
- Browser should open automatically to `http://localhost:8501`
- If not, manually open browser and go to `http://localhost:8501`

**Step 3: Prepare Screenshots**
- Have screenshot tool ready (Windows: Win+Shift+S)
- Create folder: `test_screenshots` on your desktop

---

## Test 1: User Selection

**What to Do:**
1. Look at the left sidebar
2. Find "Select User" dropdown
3. Click the dropdown
4. Select user "1"
5. Look at the main area (right side)

**What to Expect:**
- ✅ User dropdown shows user IDs (1, 2, 3, etc.)
- ✅ Main area shows user profile with:
  - User ID: 1
  - Ratings: [number]
  - Activity: Low/Medium/High

**Screenshot:** Capture as `test1_user_selection.png`

---

## Test 2: Model Selection

**What to Do:**
1. In sidebar, find "Select Model" dropdown
2. Click and see all 5 models:
   - Popularity
   - Content
   - User-Based CF
   - Item-Based CF
   - Hybrid
3. Select "Hybrid"
4. Look at "Number of recommendations" setting

**What to Expect:**
- ✅ All 5 models appear in dropdown
- ✅ Models are clearly named
- ✅ Number setting shows "10" (default)
- ✅ Can change number from 5 to 20

**Screenshot:** Capture as `test2_model_selection.png`

---

## Test 3: Generate Recommendations

**What to Do:**
1. Make sure user "1" is selected
2. Make sure "Hybrid" model is selected
3. Click the big "Generate Recommendations" button (in main area)
4. Wait for loading to finish (few seconds)

**What to Expect:**
- ✅ Loading spinner appears briefly
- ✅ Success message: "**Hybrid — [some text]**"
- ✅ 10 movie recommendations appear in a grid
- ✅ Each shows: movie poster, title, year, genres, score

**Screenshot:** Capture as `test3_recommendations.png`

---

## Test 4: Test All Models

**What to Do:**
1. Change model to "Popularity"
2. Click "Generate Recommendations"
3. Look at results
4. Change model to "Content"
5. Click "Generate Recommendations"
6. Look at results
7. Change model to "User-Based CF"
8. Click "Generate Recommendations"
9. Look at results

**What to Expect:**
- ✅ Each model generates different recommendations
- ✅ Loading spinner appears each time
- ✅ Success message appears each time
- ✅ No errors or crashes

**Screenshot:** Capture as `test4_all_models.png`

---

## Test 5: Recommendation Details

**What to Do:**
1. Generate recommendations with "Hybrid" model
2. Look at one recommendation card
3. Check the information shown:
   - Movie title and year
   - Genre tags
   - Score (number like 0.8, 0.9, etc.)
   - Explanation text
4. Click "Similar items" button on any movie

**What to Expect:**
- ✅ Movie title format: "Movie Name (Year)"
- ✅ Genres shown as tags or list
- ✅ Score between 0.0 and 1.0
- ✅ Explanation text explains why recommended
- ✅ Similar items view appears with related movies

**Screenshot:** Capture as `test5_recommendation_details.png`

---

## Test 6: Cold-Start Onboarding

**What to Do:**
1. In sidebar, find "Cold-Start Onboarding" section
2. Click "✨ Start New User Onboarding" button
3. **Step 1:** Select 3 genres (click on them)
4. Click "Next" button
5. **Step 2:** Type a movie name in search box
6. Select 2 movies you like
7. Click "Next" button
8. **Step 3:** Review your choices
9. Click "Complete Onboarding"

**What to Expect:**
- ✅ Onboarding wizard appears in main area
- ✅ Progress bar shows step 1 of 3
- ✅ Can select multiple genres
- ✅ Movie search works
- ✅ Selected movies appear in list
- ✅ Cold-start recommendations appear after completion
- ✅ Success message: "✨ Cold-Start Profile Active!"

**Screenshot:** Capture as `test6_coldstart.png`

---

## Test 7: Performance Dashboard

**What to Do:**
1. In sidebar, find "Advanced Features" section
2. Check "Show Performance Dashboard" box
3. Look at what appears in main area

**What to Expect:**
- ✅ Performance dashboard appears
- ✅ Shows charts with model performance
- ✅ Shows metrics like P@K, R@K, NDCG@K
- ✅ Charts are readable and clear
- ✅ Uncheck box to return to normal view

**Screenshot:** Capture as `test7_dashboard.png`

---

## Test 8: Model Comparison

**What to Do:**
1. Select user "1"
2. In sidebar, check "Show Model Comparison" box
3. Look at what appears in main area

**What to Expect:**
- ✅ Model comparison view appears
- ✅ Shows recommendations from different models side-by-side
- ✅ Highlights where models agree/disagree
- ✅ Shows performance comparison table
- ✅ Uncheck box to return to normal view

**Screenshot:** Capture as `test8_comparison.png`

---

## Test 9: Error Handling

**What to Do:**
1. Clear user selection (select blank if possible)
2. Try to click "Generate Recommendations"
3. Look at the message that appears

**What to Expect:**
- ✅ Helpful message appears (not technical error)
- ✅ Message tells you what to do (like "Please select a user")
- ✅ No crash or scary error message

**Screenshot:** Capture as `test9_error_handling.png`

---

## Test 10: Health Check

**What to Do:**
1. In sidebar, find "Diagnostics & Community" section
2. Click "Run System Health Check" button
3. Look at the results that appear

**What to Expect:**
- ✅ Toast notification appears (small popup)
- ✅ Shows system status (healthy/unhealthy)
- ✅ Health check results appear in expandable section
- ✅ Shows environment status, data status, model status

**Screenshot:** Capture as `test10_health_check.png`

---

## Test 11: Visual Quality Check

**What to Do:**
1. Look at the overall interface
2. Check these things:
   - Is the layout clean?
   - Are fonts readable?
   - Are colors professional?
   - Is spacing consistent?
   - Are labels clear?

**What to Expect:**
- ✅ Clean, organized layout
- ✅ Readable fonts
- ✅ Professional colors
- ✅ Consistent spacing
- ✅ Clear labels and buttons
- ✅ No spelling errors

**Screenshot:** Capture as `test11_visual_quality.png`

---

## Screenshot Checklist

After completing all tests, you should have these 11 screenshots:

1. ✅ `test1_user_selection.png`
2. ✅ `test2_model_selection.png`
3. ✅ `test3_recommendations.png`
4. ✅ `test4_all_models.png`
5. ✅ `test5_recommendation_details.png`
6. ✅ `test6_coldstart.png`
7. ✅ `test7_dashboard.png`
8. ✅ `test8_comparison.png`
9. ✅ `test9_error_handling.png`
10. ✅ `test10_health_check.png`
11. ✅ `test11_visual_quality.png`

---

## Quick Results Form

**Total Tests:** 11
**Passed:** _____
**Failed:** _____

**Overall UI Quality:** [Excellent / Good / OK / Poor]
**Ready for Submission:** [Yes / No]

**Any Issues Found:** 
_____________________________________________________
_____________________________________________________

**That's it! This simple testing covers all the essential UI/UX features.**