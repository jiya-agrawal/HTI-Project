# HTI Experiment - Data Summary Report

## Overview
This document summarizes the collected data from the Human-Technology Interaction (HTI) experiment examining the effects of different Levels of Automation (LOA) on human trust, workload, and decision-making.

---

## 📊 Dataset Characteristics

### Sample Size
- **Total Records**: 56 puzzle completions
- **Unique Participants**: 14
- **Puzzles per Participant**: 4 (one per LOA level)
- **Data Collection Period**: December 6-8, 2025 (2 days)

### Participant IDs
U20220003, U20220008, U20220027, U20220028, U20220031, U20220033, U20220041, U20220049, U20220068, U20220079, U20220098, U20230039, U20230078, U20230120

### Data Structure
- **16,384 columns** in the CSV (includes extensive logging and metadata)
- **Core columns**: 40 primary metrics
- **Key variables**: participant_id, loa_level, puzzle_id, completion_time, num_interactions, questionnaire responses

---

## 🎯 Experimental Design

### LOA Level Distribution
Each of the 4 autonomy levels was completed by all 14 participants:
- **LOA 1 (Manual)**: 14 completions - Human solves entirely
- **LOA 2 (Management by Consent)**: 14 completions - AI suggests, human approves/rejects
- **LOA 3 (Management by Exception)**: 14 completions - AI solves, human can intervene
- **LOA 4 (Full Automation)**: 14 completions - AI provides final solution

### Puzzle Distribution
12 unique puzzles (IDs 101-112) were used:
- Most frequently used: Puzzle 110 (8 times), Puzzle 107 (7 times), Puzzle 106 (6 times)
- Least used: Puzzle 108 (2 times)

### AI Faulty Condition
- **Non-faulty trials**: 47 (83.9%)
- **Faulty trials**: 9 (16.1%)

---

## ⏱️ Performance Metrics

### Completion Time (seconds)
- **Overall Mean**: 295.98s (~4.9 minutes)
- **Median**: 283.41s
- **Standard Deviation**: 122.00s
- **Range**: 63.08s - 632.45s (10x variation)

#### Completion Time by LOA Level
| LOA Level | Mean (s) | Median (s) | Std Dev (s) |
|-----------|----------|------------|-------------|
| LOA 1     | 317.08   | 308.23     | 128.13      |
| LOA 2     | 294.05   | 278.61     | 100.38      |
| LOA 3     | 325.61   | 271.83     | 153.16      |
| LOA 4     | 247.19   | 274.59     | 95.00       |

**Key Finding**: LOA 4 (Full Automation) showed fastest mean completion time, but LOA 3 had highest variability.

---

## 🖱️ Interaction Metrics

### Number of Interactions
- **Overall Mean**: 17.59 interactions per puzzle
- **By LOA Level**:

| LOA Level | Mean | Median | Std Dev |
|-----------|------|--------|---------|
| LOA 1     | 24.43| 18.5   | 16.82   |
| LOA 2     | 25.36| 18.0   | 16.55   |
| LOA 3     | 14.71| 7.5    | 13.85   |
| LOA 4     | 5.86 | 2.0    | 6.55    |

**Key Finding**: Interaction count decreases dramatically with increasing automation (LOA 1/2 ~25 interactions vs LOA 4 ~6 interactions).

---

## ✅ Correctness & Decision-Making

### Overall Correctness Rate
**82.1%** of puzzles solved correctly

### Correctness by LOA Level
| LOA Level | Correctness Rate |
|-----------|------------------|
| LOA 1     | 71.4%            |
| LOA 2     | 71.4%            |
| LOA 3     | **100.0%**       |
| LOA 4     | 85.7%            |

**Critical Finding**: LOA 3 (Management by Exception) achieved perfect correctness, suggesting optimal balance between automation and human oversight.

### Behavioral Patterns

#### LOA 2 - Acceptance Rate
- **AI Advice Accepted**: 0.0% 
- *Note: This unexpectedly low rate suggests participants may have preferred manual control or lacked trust in AI suggestions*

#### LOA 3 - Override Behavior
- **Override Rate**: 28.6%
- Participants intervened in approximately 1 out of 4 puzzles when AI provided automated solutions

---

## 🧠 Trust Metrics

### Pre-Task Trust Scores (1-7 scale, n=42)
| Question | Mean | Std Dev | Median | Range   |
|----------|------|---------|--------|---------|
| Q1       | 3.60 | 0.66    | 4.0    | 2.0-5.0 |
| Q2       | 3.45 | 0.63    | 4.0    | 2.0-4.0 |
| Q3       | 3.48 | 0.71    | 3.5    | 2.0-5.0 |
| Q4       | 3.67 | 0.72    | 4.0    | 2.0-5.0 |
| Q5       | 3.62 | 0.49    | 4.0    | 3.0-4.0 |
| **Average** | **3.56** | | | |

### Post-Task Trust Scores (1-7 scale, n=42)
| Question | Mean | Std Dev | Median | Range   |
|----------|------|---------|--------|---------|
| Q1       | 3.55 | 1.04    | 4.0    | 1.0-5.0 |
| Q2       | 3.50 | 1.09    | 4.0    | 1.0-5.0 |
| Q3       | 3.76 | 0.93    | 4.0    | 1.0-5.0 |
| Q4       | 3.36 | 1.01    | 4.0    | 1.0-5.0 |
| Q5       | 3.52 | 1.06    | 4.0    | 1.0-5.0 |
| **Average** | **3.54** | | | |

**Key Finding**: Minimal change in trust from pre (3.56) to post (3.54), but increased variability post-task (higher std dev), suggesting divergent experiences across LOA levels.

---

## 🎯 Awareness Quiz Scores

Awareness quiz measured participants' understanding of AI behavior and system state (0-2 scale, n=56):

| Question | Mean | Std Dev | Median |
|----------|------|---------|--------|
| Q1       | 1.73 | 0.56    | 2.0    |
| Q2       | 1.59 | 0.76    | 2.0    |
| Q3       | 1.43 | 0.71    | 2.0    |
| Q4       | 1.14 | 0.86    | 1.0    |
| Q5       | 1.14 | 0.90    | 1.0    |
| **Average** | **1.41** | | |

**Interpretation**: Moderate awareness levels (70.5% correct on average), with decreasing accuracy from Q1 to Q5, suggesting increasing difficulty or decreased attention to system details.

---

## 📈 Productivity Metrics

Self-reported productivity measures (1-5 scale, n=56):

| Question | Mean | Std Dev | Median | Interpretation |
|----------|------|---------|--------|----------------|
| Q1       | 2.82 | 1.05    | 3.0    | Task efficiency |
| Q2       | 2.77 | 1.10    | 3.0    | Workload perception |
| Q3       | 2.88 | 1.15    | 3.0    | Satisfaction |
| Q4       | 3.88 | 0.99    | 4.0    | Confidence |
| **Average** | **3.08** | | | |

**Key Finding**: Moderate productivity scores overall (~3/5), with notably higher confidence (Q4: 3.88) compared to other dimensions, suggesting participants felt more confident than they felt efficient.

---

## 🔍 AI Faulty Condition Impact

### Completion Time
| Condition | Mean (s) | Median (s) |
|-----------|----------|------------|
| Non-faulty| 293.10   | 286.25     |
| Faulty    | 311.01   | 262.92     |

### Interactions
| Condition | Mean | Median |
|-----------|------|--------|
| Non-faulty| 16.79| 15.0   |
| Faulty    | 21.78| 13.0   |

**Finding**: Faulty AI trials took longer on average (+6%) and required more interactions (+30%), though median interaction count was lower, suggesting high variability in how participants dealt with AI errors.

---

## 👥 Participant-Level Variability

### Completion Time Ranges
- **Fastest participant (U20230039)**: 175.08s average
- **Slowest participant (U20220033)**: 399.55s average
- **Factor difference**: 2.3x

### Interaction Patterns
- **Least interactive (U20220079)**: 8.5 interactions average
- **Most interactive (U20220031)**: 34.25 interactions average
- **Factor difference**: 4x

### Individual Consistency (Std Dev of completion times)
- **Most consistent (U20220027)**: 13.66s std dev
- **Most variable (U20220031)**: 202.23s std dev

**Key Finding**: Substantial individual differences in both speed and interaction style, highlighting the importance of individual-level analysis.

---

## 🔑 Key Research Findings Summary

### 1. **LOA Impact on Performance**
   - LOA 3 achieved perfect accuracy (100%) despite not being fully automated
   - LOA 4 was fastest but not most accurate
   - Human-led approaches (LOA 1 & 2) showed similar performance (~71% accuracy)

### 2. **Trust Calibration**
   - Minimal overall trust change pre-to-post
   - Increased post-task variability suggests different LOAs affected trust differently
   - Low AI advice acceptance (0%) in LOA 2 indicates potential over-distrust

### 3. **Automation Paradox**
   - More automation ≠ better performance
   - "Sweet spot" at LOA 3 (shared control with human oversight)
   - LOA 4 sacrificed some accuracy for speed

### 4. **Individual Differences**
   - 2-4x variation in completion times and interaction patterns
   - Some participants consistently fast/slow across conditions
   - Suggests importance of adaptive automation

### 5. **Awareness-Performance Gap**
   - Moderate awareness scores (70%) despite 82% correctness
   - Participants may be performing without full system understanding
   - Raises concerns about appropriate reliance on automation

---

## 📝 Data Quality Notes

- **Missing Data**: Pre/post trust scores available for 42/56 records (75%)
- **Awareness & Productivity**: Complete data for all 56 records
- **Timeline**: Compressed 2-day data collection period
- **Balance**: Perfect balance across LOA levels (14 each)

---

## 🎓 Implications for Research

This dataset provides evidence for:
1. **Non-linear relationship** between automation level and performance
2. **Critical role of human oversight** (LOA 3 success)
3. **Trust-performance dissociation** (high performance, modest trust)
4. **Individual adaptation strategies** to different automation levels
5. **Need for calibrated trust** (especially in LOA 2)

---

## 📊 Recommended Analyses

### Immediate Priority:
1. **Within-subjects ANOVA** - LOA effect on completion time & accuracy
2. **Trust trajectory analysis** - Pre vs post by LOA level
3. **Interaction pattern clustering** - Identify behavioral profiles
4. **Faulty AI × LOA interaction** - How errors affect trust at each level

### Secondary Analyses:
5. Mixed-effects models accounting for individual differences
6. Temporal analysis of learning effects across puzzles
7. Awareness-correctness correlation
8. Decision latency as trust proxy

---

*Report generated: December 8, 2025*  
*Data spans: 56 puzzle completions, 14 participants, 4 LOA conditions*
