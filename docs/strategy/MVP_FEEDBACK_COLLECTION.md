# MVP Feedback Collection Plan

**Purpose:** Systematically gather coach feedback to inform Phase 2 feature prioritization.

**Document Date:** November 26, 2025

______________________________________________________________________

## Feedback Collection Strategy

**Timeline:** Week 4-5 (2 weeks)
**Target:** 5-10 coaches
**Method:** Mix of interviews and surveys

**Output:** Structured feedback data to drive Phase 2 decisions (real-time vs running vs API)

______________________________________________________________________

## Coach Recruitment

### Who to Target

**Ideal Coach Profile:**

- Jump sport background (CrossFit, track & field, basketball)
- Works with athletes (team or individual coaching)
- Uses video for athlete feedback
- Has smartphone + laptop (can upload videos)
- Willing to spend 15 minutes testing MVP

### Where to Find Coaches

1. **Personal Network**

   - LinkedIn: Search "CrossFit coach" or "track & field coach"
   - Social media: CrossFit communities, running clubs
   - Forums: Reddit r/crossfit, track & field communities

1. **Organized Communities**

   - CrossFit boxes (contact local affiliates)
   - University track programs
   - Basketball coaching forums

1. **Direct Outreach**

   - Email template below

### Email Template

```
Subject: Testing new CMJ analysis tool (5 min feedback)

Hi [Coach Name],

I'm building a simple tool that analyzes counter-movement jump videos and
provides metrics (jump height, flight time, triple extension, etc.) for coaches.

Would you be willing to:
1. Try uploading a 1-2 jump video (takes 5 min)
2. Look at the metrics
3. Answer 5 quick questions about what you'd find useful? (10 min)

Total time: ~15 minutes. Help us build the right features.

Link: [MVP URL]

Thanks,
[Your name]
```

______________________________________________________________________

## Feedback Collection Script

### Part 1: Basic Usage (Embedded Analytics, Auto-Tracked)

When coaches use the MVP, track:

- [ ] Videos uploaded
- [ ] Videos analyzed successfully
- [ ] Time to analyze
- [ ] Errors encountered
- [ ] Features clicked on
- [ ] Export format used

### Part 2: Interview / Survey Questions

**Use this structured script to collect feedback:**

#### Question 1: Accuracy & Trust

> "Looking at the metrics provided, do they seem accurate for your athletes? Why or why not?"

**Track:**

- [ ] "Yes, looks good"
- [ ] "Pretty close, but \[specific issue\]"
- [ ] "Not accurate - \[reason\]"

**Follow-up if uncertain:** "Would you trust these metrics for coaching decisions?"

______________________________________________________________________

#### Question 2: Current Use Case

> "How do you currently analyze jump videos? What's missing in your current workflow?"

**Track:**

- [ ] "I use \[app/tool\] currently"
- [ ] "I just watch and eyeball it"
- [ ] "I don't analyze videos"
- [ ] "I use Dartfish/VueMotion/etc"

**Follow-up:** "What would make analyzing videos easier for you?"

______________________________________________________________________

#### Question 3: Feature Priorities (CRITICAL for Phase 2 decision)

> "Which of these features would be most useful to you?"

**Options (present one at a time, ask to rank):**

1. **Real-Time Feedback** - See metrics live while athlete is jumping

   - "I could give instant feedback during training session"
   - Trade-off: More complex, takes longer to build
   - Estimated availability: 3-4 weeks

1. **Running Gait Analysis** - Same metrics for running videos

   - "I work with runners and want to analyze running form"
   - Trade-off: Different sport, may not be relevant to jumpers
   - Estimated availability: 2-3 weeks

1. **Integration with My App** - API so the tool can work within your existing platform

   - "We want to embed this in our coaching app/system"
   - Trade-off: Requires technical setup from your end
   - Estimated availability: 2 weeks

1. **Better UI/UX** - Improve this interface, add more details

   - "The current interface needs improvement"
   - Trade-off: Slower to ship new features
   - Estimated availability: 1-2 weeks

**Track:** Ranking order for each coach

______________________________________________________________________

#### Question 4: Pricing & Willingness to Pay

> "If this tool was available today, would you use it?"

**Options:**

- [ ] "Yes, free or cheap only"
- [ ] "Yes, if \<$50/month"
- [ ] "Yes, even if $100-200/month"
- [ ] "Yes, if integrated with my platform ($500+/month)"
- [ ] "No, not interested"

**Follow-up:** "What's your budget for coaching tools?"

______________________________________________________________________

#### Question 5: Open Feedback

> "What else should we build to make this useful for you?"

**Track:** Direct feedback, new ideas, pain points

**Examples of answers:**

- "I need multiple athlete comparison"
- "I need video slow-motion/annotation tools"
- "I need mobile app, not web"
- "I need \[specific metric\] tracked"

______________________________________________________________________

## Feedback Synthesis Template

**Use this after collecting feedback from all coaches:**

```markdown
## MVP Feedback Synthesis (Date: _____)

### Summary Statistics
- Coaches interviewed: ___ / 10
- Videos analyzed: ___ total
- Average analysis time: ___ seconds
- Errors/crashes: ___ incidents

### Accuracy Trust Level
- Trusted metrics: ___ coaches
- Somewhat trusted: ___ coaches
- Don't trust: ___ coaches

**Specific accuracy concerns:**
- [Coach feedback on what seemed wrong]

### Current Workflow
- Using [tool name]: ___ coaches
- Manual analysis: ___ coaches
- Not analyzing: ___ coaches

### Feature Priority Ranking

**Real-Time Feedback:**
- Coaches requesting: ___ (X%)
- High priority: [Coach names]
- Low priority: [Coach names]

**Running Gait:**
- Coaches requesting: ___ (X%)
- High priority: [Coach names]
- Low priority: [Coach names]

**API/Integration:**
- Coaches requesting: ___ (X%)
- Specific partners identified: [List]
- Use cases: [List]

**Other Features:**
- Mentioned by: ___ coaches
- Top request: [Feature name]

### Willingness to Pay
- Free only: ___ coaches
- <$50/mo: ___ coaches
- $100-200/mo: ___ coaches
- $500+/mo: ___ coaches

### Recommendation: Phase 2 Priority

**PRIMARY:** [Feature] (requested by X coaches, strongest demand)
**SECONDARY:** [Feature] (requested by X coaches, good signal)
**TERTIARY:** [Feature] (requested by X coaches, could be future)

**Rationale:**
- [Why primary feature won]
- [Market opportunity]
- [Ease of implementation]

### Next Steps
1. Implement [Primary Feature]
2. Target launch: [Date]
3. Re-validate with coaches after Phase 2 launch
```

______________________________________________________________________

## Feedback Collection Schedule

### Week 4 (Days 1-3): Recruitment

- [ ] Identify target coaches
- [ ] Send outreach emails
- [ ] Confirm participation from 5-10 coaches

### Week 4 (Days 4-5): Early Feedback

- [ ] First coaches test MVP
- [ ] Auto-track usage metrics
- [ ] Conduct informal interviews

### Week 5 (Days 1-3): Final Testing

- [ ] Remaining coaches test MVP
- [ ] Conduct formal interviews with all coaches
- [ ] Collect survey responses

### Week 5 (Day 4-5): Synthesis & Decision

- [ ] Compile all feedback
- [ ] Fill out feedback synthesis template
- [ ] Make Phase 2 decision (checkpoint 2, decision gate 1)

______________________________________________________________________

## Interview Logistics

### Video Call Setup (Recommended)

**Tool:** Zoom, Google Meet, or Calendly
**Duration:** 15-20 minutes per coach
**Format:**

1. Greeting + context (2 min)
1. MVP demo/walkthrough (5 min)
1. Questions 1-5 (10 min)
1. Open feedback (2-3 min)

### Compensation

**Optional approaches to encourage participation:**

- Free 3-month subscription to Phase 2 feature
- 1-on-1 coaching consultation (if applicable)
- Acknowledgment in launch materials ("Early Advisors")
- None (passion for the sport may be enough)

### Follow-Up

Send thank you email with:

- Results summary (when available)
- "Your feedback led us to \[Feature X\]"
- Link to product launch when Phase 2 ships

______________________________________________________________________

## Key Success Metrics

**MVP Feedback Collection Success = :**

- [ ] 5+ coaches tested MVP
- [ ] Clear consensus on Phase 2 feature priority
- [ ] Evidence supporting recommendation
- [ ] At least 3 coaches willing to continue testing Phase 2

**If feedback is inconclusive:**

- Extend feedback collection by 1 week
- Recruit 5 more coaches
- Focus questions on most disputed feature

______________________________________________________________________

## References

- MVP Validation Checkpoints: `MVP_VALIDATION_CHECKPOINTS.md`
- Strategic Summary: `1-STRATEGIC_SUMMARY.md`
- GitHub Issues: #10, #11, #12, #13, #14

______________________________________________________________________

**Document Status:** ACTIVE

**Created:** November 26, 2025
**Last Updated:** November 26, 2025
