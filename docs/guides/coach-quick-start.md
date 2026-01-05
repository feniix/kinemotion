# Coach Quick Start Guide

**Analyze your athletes' jumps in seconds. No wearables. No markers. Just video.**

______________________________________________________________________

## What is Kinemotion?

Kinemotion analyzes jump performance from video. Record your athlete, upload the video, and get immediate metrics on jump height, power, and technique.

**Supported jumps:**

- **Counter Movement Jump (CMJ)** - Measure explosive power from a standing position
- **Drop Jump** - Measure reactive strength and ground contact time

**Get started at:** https://kinemotion.vercel.app

______________________________________________________________________

## Recording a Good Video

The quality of your analysis depends on your video. Follow these guidelines:

### Camera Position ✅

| Jump Type     | Camera Angle                  | Distance | Height          |
| ------------- | ----------------------------- | -------- | --------------- |
| **CMJ**       | 45° oblique (from front-side) | 3-5m     | Hip level (~1m) |
| **Drop Jump** | 45° oblique (from front-side) | 3-5m     | Hip level (~1m) |

**Why 45°?** This angle lets the AI see both legs clearly. A pure side view (90°) causes the legs to overlap, making tracking unreliable.

See [Camera Setup Guide](camera-setup.md) for detailed visual guide.

### Framing ✅

- **Full body visible** - Head to feet throughout the entire jump
- **Stable camera** - Use a tripod or prop your phone steadily
- **Landscape orientation** - Hold phone sideways (horizontal)
- **Good lighting** - Avoid backlighting (athlete between camera and sun)

### What to Avoid ❌

- Front view (directly facing the athlete)
- Hand-held camera (too shaky)
- Camera too low or too high
- Poor lighting or shadows on the athlete

### Quick Checklist

Before you record:

- [ ] Camera at 45° angle to athlete
- [ ] 3-5 meters away
- [ ] Hip height (~1m off ground)
- [ ] Full body in frame (head to feet)
- [ ] Phone in landscape (horizontal)
- [ ] Camera stable (tripod or surface)
- [ ] Good lighting

______________________________________________________________________

## Using Kinemotion

### 1. Go to the Website

Visit **https://kinemotion.vercel.app** and sign in with your email.

### 2. Select Jump Type

| Button        | Jump Type             | What It Measures              |
| ------------- | --------------------- | ----------------------------- |
| **CMJ**       | Counter Movement Jump | Explosive power from standing |
| **Drop Jump** | Drop from box         | Reactive strength, quickness  |

### 3. Upload Your Video

- Click **Choose File** or drag and drop your video
- Supported formats: MP4, MOV, AVI
- Maximum size: 500MB
- Typical video: 10-30 seconds

### 4. Click Analyze

Wait 10-30 seconds for processing. You'll see:

- Real-time progress
- Processing status
- Results when complete

### 5. Review Results

Your analysis includes:

| Metric           | What It Tells You                           |
| ---------------- | ------------------------------------------- |
| **Jump Height**  | How high the athlete jumped (meters)        |
| **Air Time**     | Time spent airborne (seconds)               |
| **Depth**        | How deep they squatted before jumping (CMJ) |
| **Contact Time** | Time on ground after landing (Drop Jump)    |
| **RSI**          | Reactive Strength Index (Drop Jump)         |

______________________________________________________________________

## Understanding the Metrics

### Jump Height Reference Values

> **⚠️ Note on Data Bias:** Adult normative values below may be **optimistic by 5-10 cm** for truly sedentary populations. Most published norms study physically active adults (PE students, gym-goers), not the general population. Use these as athletic benchmarks, not population averages.
>
> Youth data (13-16 years) is more accurate as it specifically studied untrained adolescents (n=3,705).

#### Adult Men (Untrained to Trained)

| Rating            | Jump Height       | What It Means               |
| ----------------- | ----------------- | --------------------------- |
| **Excellent**     | >70 cm (28")      | Elite-level power           |
| **Very Good**     | 61-70 cm (24-28") | Competitive athlete         |
| **Above Average** | 51-60 cm (20-24") | Well-trained                |
| **Average**       | 41-50 cm (16-20") | Recreational athlete        |
| **Below Average** | 31-40 cm (12-16") | Untrained                   |
| **Poor**          | 21-30 cm (8-12")  | Significant training needed |

#### Adult Women (Untrained to Trained)

> **⚠️ Note:** Same bias caveat as above - norms likely reflect active women, not truly sedentary populations.

| Rating            | Jump Height       | What It Means               |
| ----------------- | ----------------- | --------------------------- |
| **Excellent**     | >60 cm (24")      | Elite-level power           |
| **Very Good**     | 51-60 cm (20-24") | Competitive athlete         |
| **Above Average** | 41-50 cm (16-20") | Well-trained                |
| **Average**       | 31-40 cm (12-16") | Recreational athlete        |
| **Below Average** | 21-30 cm (8-12")  | Untrained                   |
| **Poor**          | 11-20 cm (4-8")   | Significant training needed |

#### Youth: Male Athletes (13-16 years, Untrained)

| Age             | Talent (95th) | Excellent (75th) | Good (50th) | Average |
| --------------- | ------------- | ---------------- | ----------- | ------- |
| **13-14 years** | ≥47 cm        | ≥37 cm           | ≥30 cm      | ~30 cm  |
| **15-16 years** | ≥57 cm        | ≥47 cm           | ≥39 cm      | ~38 cm  |

#### Youth: Female Athletes (13-16 years, Untrained)

| Age             | Talent (95th) | Excellent (75th) | Good (50th) | Average |
| --------------- | ------------- | ---------------- | ----------- | ------- |
| **13-14 years** | ≥40 cm        | ≥32 cm           | ≥26 cm      | ~27 cm  |
| **15-16 years** | ≥42 cm        | ≥33 cm           | ≥28 cm      | ~28 cm  |

#### Elite Professional Athletes

| Sport                  | Level   | Jump Height          |
| ---------------------- | ------- | -------------------- |
| **NBA Basketball**     | Average | 71-81 cm (28-32")    |
| **NBA Basketball**     | Elite   | 89-102+ cm (35-40+") |
| **NFL Football**       | Average | 64-76 cm (25-30")    |
| **NFL Football**       | Elite   | 89-107 cm (35-42")   |
| **Volleyball (Men)**   | Elite   | 81-91 cm (32-36")    |
| **Volleyball (Women)** | Elite   | 66-76 cm (26-30")    |

#### Age-Related Decline (Adults 30+)

> **Performance peaks at 20-29 years**, then declines ~1% per year. Even elite masters athletes show this pattern - it's not just about "getting out of shape," but physiological changes in muscle mass and quality.

**Men by Age Group:**

| Rating        | 20-29  | 30-39  | 40-49  | 50-59  | 60-69  |
| ------------- | ------ | ------ | ------ | ------ | ------ |
| **Excellent** | ≥58 cm | ≥52 cm | ≥43 cm | ≥41 cm | ≥33 cm |
| **Very Good** | 54-57  | 46-51  | 36-42  | 34-40  | 29-32  |
| **Good**      | 48-53  | 40-45  | 32-35  | 28-33  | 25-28  |
| **Fair**      | 42-47  | 31-39  | 26-31  | 18-27  | 18-24  |

**Women by Age Group:**

| Rating        | 20-29  | 30-39  | 40-49  | 50-59  | 60-69  |
| ------------- | ------ | ------ | ------ | ------ | ------ |
| **Excellent** | ≥38 cm | ≥36 cm | ≥31 cm | ≥25 cm | ≥19 cm |
| **Very Good** | 34-37  | 32-35  | 27-30  | 21-24  | 15-18  |
| **Good**      | 29-33  | 28-31  | 23-26  | 16-20  | 11-14  |
| **Fair**      | 25-28  | 24-27  | 18-22  | 10-15  | 7-10   |

**Decline from Peak (Men):**

- 30-39: -6 cm (10%)
- 40-49: -15 cm (26%)
- 50-59: -17 cm (29%)
- 60-69: -25 cm (43%)

### Air Time

| Jump Height | Air Time |
| ----------- | -------- |
| 30 cm       | ~0.50s   |
| 40 cm       | ~0.57s   |
| 50 cm       | ~0.64s   |

### Drop Jump Reference Values

> **What is RSI?** The Reactive Strength Index measures how efficiently an athlete converts ground contact into upward force. Formula: **Jump Height (m) ÷ Ground Contact Time (s)**

#### RSI Classification (Drop Jump from 30-40 cm box)

| Level         | RSI Score | What It Means              | Plyometric Readiness                |
| ------------- | --------- | -------------------------- | ----------------------------------- |
| **Excellent** | 2.5+      | Elite reactive ability     | Ready for intensive plyometrics     |
| **Very Good** | 2.0 - 2.5 | Strong plyometric capacity | Ready for moderate-high intensity   |
| **Good**      | 1.5 - 2.0 | Adequate reactive strength | Ready for moderate intensity        |
| **Fair**      | \< 1.5    | Needs development          | Focus on strength + basic technique |

**Sources:** Flanagan (2021), Young (1995) - based on drop jumps with hands on hips

#### RSI by Athlete Profile

| Athlete Type                                | Typical RSI | Notes                                |
| ------------------------------------------- | ----------- | ------------------------------------ |
| **Elite Sprinters**                         | 2.8 - 3.5+  | World-class acceleration ability     |
| **Power Athletes** (volleyball, basketball) | 2.3 - 3.0   | High ceiling for explosive movements |
| **Team Sport Athletes** (soccer, rugby)     | 1.8 - 2.5   | Variable by position and training    |
| **Recreational Athletes**                   | 1.2 - 1.8   | Room for improvement with training   |
| **Untrained**                               | 0.8 - 1.4   | Technique limits often dominate      |

#### RSI by Sex (Collegiate/NCAA Level)

**Based on RSImod (Jump Height ÷ Time to Takeoff) from 151 NCAA Division I athletes:**

| Percentile               | Male RSImod | Female RSImod |
| ------------------------ | ----------- | ------------- |
| **97th (Elite)**         | 0.63        | 0.50          |
| **90th (Excellent)**     | 0.55        | 0.43          |
| **75th (Very Good)**     | 0.49        | 0.38          |
| **50th (Average)**       | 0.42        | 0.31          |
| **25th (Below Average)** | 0.35        | 0.25          |

*Note: RSImod values differ from standard RSI - do not compare directly. Source: Sole et al. (2018)*

#### Age-Related Differences (Elite Female Footballers)

| Age Group  | RSI Level | Difference                  |
| ---------- | --------- | --------------------------- |
| **Senior** | Highest   | Baseline                    |
| **U19**    | Lower     | Large effect size vs Senior |
| **U17**    | Lowest    | Large effect size vs Senior |

**Key finding:** Even at elite youth levels, RSI increases with maturation. Senior players show significantly higher reactive strength than U17/U19. *Source: Doyle et al. (2021)*

#### Ground Contact Time (GCT) Reference Values

GCT is a key component of RSI. Shorter contact time = better reactive ability.

| Classification | GCT          | What It Means                        |
| -------------- | ------------ | ------------------------------------ |
| **Elite**      | \< 180 ms    | Exceptional stretch-shortening cycle |
| **Very Good**  | 180 - 200 ms | Fast SSC utilization                 |
| **Good**       | 200 - 220 ms | Adequate reactive ability            |
| **Average**    | 220 - 250 ms | Room for improvement                 |
| **Developing** | > 250 ms     | Focus on technique first             |

**Practical note:** GCT > 250ms indicates the athlete is no longer using the fast stretch-shortening cycle.

#### Optimal Drop Height by RSI Level

The "optimal" drop height is where the athlete achieves their **best RSI score**, not the highest box.

| RSI Level     | Optimal Drop Height | Guidance                                 |
| ------------- | ------------------- | ---------------------------------------- |
| **\< 1.0**    | 15-20 cm            | Focus on landing mechanics first         |
| **1.0 - 1.5** | 20-30 cm            | Build basic reactive strength            |
| **1.5 - 2.0** | 30-40 cm            | Standard testing height                  |
| **2.0+**      | 30-45 cm            | Test incremental heights to find optimum |

**Important:** If increasing box height causes GCT to exceed 250ms, the height is too high for that athlete.

#### Drop Jump vs CMJ: When to Use Each

| Test          | Best For                    | What It Measures                        |
| ------------- | --------------------------- | --------------------------------------- |
| **CMJ**       | Overall explosive power     | Force production + range of motion      |
| **Drop Jump** | Reactive ability, quickness | Fast SSC, ground contact efficiency     |
| **Use Both**  | Complete athlete profile    | Different qualities, complementary data |

**Interpretation:**

- **High CMJ / Low RSI:** Strong but "slow" - benefit from plyometric focus
- **Low CMJ / High RSI:** Elastic but weak - benefit from strength focus

#### RSI-Based Training Decisions

| RSI Score     | Interpretation              | Training Focus                        |
| ------------- | --------------------------- | ------------------------------------- |
| **\< 1.0**    | Not ready for plyometrics   | Strength base, landing mechanics      |
| **1.0 - 1.5** | Plyo beginner               | Low-intensity plyometrics + strength  |
| **1.5 - 2.0** | Developing reactive ability | Moderate plyometrics, progress volume |
| **2.0 - 2.5** | Good reactive capacity      | Higher intensity plyometrics          |
| **2.5+**      | Elite reactive ability      | Sport-specific power, maintenance     |

### Countermovement Depth (CMJ only)

How deep the athlete squats before jumping:

- **Too shallow (\< 20 cm)**: Not using full range of motion
- **Optimal (20 - 35 cm)**: Good balance of depth and speed
- **Too deep (> 40 cm)**: May be slowing down the jump

______________________________________________________________________

## Tips for Better Analysis

### For Accurate Results

1. **Consistent setup** - Use the same camera position each time for comparable results
1. **Multiple attempts** - Record 3-5 jumps and use the best result
1. **Rest between attempts** - 1-2 minutes rest ensures maximum effort
1. **Standardized instructions** - Tell athletes: "Jump as high as you can"

### Tracking Progress

- **Baseline first** - Record initial measurements before training
- **Test every 4-6 weeks** - Too frequent testing doesn't show meaningful change
- **Same conditions** - Test at similar time of day, similar fatigue level

### What to Do with Poor Results

| Issue                  | Possible Cause               | Solution                          |
| ---------------------- | ---------------------------- | --------------------------------- |
| Low jump height        | Fatigue, poor technique      | Rest, review jump mechanics       |
| Very long contact time | Hesitation, landing softness | Practice explosive ground contact |
| Inconsistent results   | Variable effort, setup       | Standardize testing protocol      |

______________________________________________________________________

## Troubleshooting

### "Analysis Failed" Error

**Possible causes:**

- Video too short or doesn't show complete jump
- Camera angle too far from 45°
- Poor lighting or blurry video
- Athlete not fully visible in frame

**Try:**

- Re-record with better camera setup
- Ensure full body is visible
- Improve lighting

### Unexpected Results

**If jump height seems too high or too low:**

- Check camera was level (not tilted up/down)
- Verify athlete was fully in frame
- Ensure video wasn't recorded from an angle

**If RSI seems off (Drop Jump):**

- Confirm athlete dropped off the box (didn't step down)
- Check landing was captured fully
- Verify box height was appropriate for athlete level

______________________________________________________________________

## Exporting Results

After analysis, you can:

- **Screenshot** - Capture results for your records
- **Download CSV** - Export data for spreadsheet analysis (coming soon)
- **Compare over time** - Track athlete progress across sessions

______________________________________________________________________

## Need Help?

**Questions or feedback?** Email us at support@kinemotion.dev

**Found a bug?** Report it at github.com/feniix/kinemotion/issues

______________________________________________________________________

*Last updated: January 2025*
*Kinemotion v1.0 - Video-based jump analysis for coaches*
