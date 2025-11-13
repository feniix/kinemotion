# Kinemotion Presentation Speaker Script

## Complete Speaking Notes and Demonstration Guide

______________________________________________________________________

## Pre-Presentation Setup (Remote/Zoom)

### Technical Checklist for Screen Sharing

- [ ] Test Zoom screen sharing in advance
- [ ] Increase all font sizes (terminal: 18pt+, IDE: 16pt+)
- [ ] Close all unnecessary applications/tabs
- [ ] Clear desktop of any sensitive information
- [ ] Disable all notifications (Slack, email, etc.)
- [ ] Demo videos downloaded locally (samples folder)
- [ ] Terminal open with kinemotion installed
- [ ] Python environment activated
- [ ] IDE/VS Code with example code ready
- [ ] Test audio with headphones to avoid echo
- [ ] Have backup slides in cloud (Google Drive/OneDrive)
- [ ] Verify recording permissions with meeting host

### Sample Files Ready

- `samples/cmjs/` - CMJ videos for demo
- `samples/dropjumps/` - Drop jump videos
- Debug output video prepared

______________________________________________________________________

## SLIDE 1: Title Slide (30 seconds)

### Opening Hook

"Hey everyone, can you all see my screen okay? Great. So I've been working on this hobby project called Kinemotion. Quick question for the chat - has anyone here ever tried to measure their vertical jump or analyze sports performance from video? Just drop a yes or no in the chat."

\[Pause for chat responses\]

"Right, for those who have, you know it's either super expensive equipment or tedious manual work. That's exactly why I started this project."

### Introduction

"Kinemotion is an open-source tool I've been building that takes properly recorded smartphone videos and extracts athletic performance metrics automatically. It's been a fascinating technical challenge combining computer vision, biomechanics, and signal processing."

### Set Expectations

"Over the next 30 minutes, I'll walk you through the technical approach, show live demos, and discuss some interesting challenges I've encountered. This is very much a work in progress, so I'd love your feedback and ideas."

______________________________________________________________________

## SLIDE 2: The Challenge (3 minutes)

### Problem Context

"Let's talk about the current landscape of jump analysis. You've got expensive lab equipment on one end - force plates at $10-50k, motion capture systems in the six figures. Then you've got the software solutions that try to democratize this."

### Existing Tools Experience

"So I tried My Jump Lab - you might have heard of it, it's pretty popular. Phone-based app, supposed to be automated. But here's what I found: it failed on several of my recordings. Sometimes the detection was inconsistent, other times I still had to manually select frames. Not exactly the automated solution it promises to be."

"Then there's Tracker from Open Source Physics - and don't get me wrong, [Tracker](https://opensourcephysics.github.io/tracker-website/) is fantastic for what it does. It's incredibly powerful for physics education and detailed analysis. But the learning curve is steep, and you're manually tracking points frame by frame. Great for a physics lab, not so great when you have 50 athletes to assess."

### The Gap

"So we have expensive hardware that works perfectly but costs a fortune, and software that's either unreliable or requires extensive manual work. That's the gap I'm trying to fill."

### Personal Motivation

"What got me started was my own training frustration. I wanted to track my vertical jump progress. My Jump Lab kept failing on my videos, and I wasn't about to spend hours in Tracker for each jump. I figured - I know computer vision, I know Python, MediaPipe exists - why not build something that actually works automatically? Classic engineer approach, right?"

______________________________________________________________________

## SLIDE 3: Solution Overview (3 minutes)

### Transition

"So where does Kinemotion fit in this landscape? Let me show you a comparison."

### Positioning Against Competitors

"Here's the key difference: My Jump Lab tries to be automated but often isn't reliable. Tracker is reliable but completely manual. Kinemotion aims to be both automated AND reliable."

"Look at this comparison table. We're fully automated like My Jump Lab claims to be, but we're also open source like Tracker. You can see exactly how it works, modify it, extend it. And unlike both, we support batch processing - analyze 100 videos in parallel."

### Technical Advantages

"The technical secret sauce is MediaPipe - Google's pose detection that tracks 33 body landmarks automatically. No manual point selection needed. The system auto-tunes to your video quality and framerate."

"We use different algorithms for different jump types. Drop jumps use forward search, CMJs use backward search from the peak. This isn't a one-size-fits-all solution - it's tailored to the biomechanics of each movement."

### Realistic Positioning

"Now, I'm not claiming Kinemotion is perfect. It's not validated against force plates yet. But in my experience, it's been more reliable than My Jump Lab and infinitely faster than Tracker. It fills that gap between 'doesn't work' and 'takes forever'."

______________________________________________________________________

## SLIDE 4: Technical Architecture (3 minutes)

### High-Level Flow

"Let me walk you through the technical pipeline. It starts with your video file - any standard format works."

### Processing Steps

"MediaPipe processes each frame, giving us 3D coordinates for body landmarks - ankles, knees, hips, shoulders, and more."

"Now here's a key challenge - pose detection is noisy. The coordinates jump around frame to frame. We apply Savitzky-Golay filtering - it's a mathematical technique that smooths the data while preserving important features like velocity peaks. Think of it as removing the jitter while keeping the actual movement intact. This same technique is used in aerospace for smoothing satellite trajectories."

### Algorithm Innovation

"Here's where it gets interesting. For CMJ analysis, we use a backward search algorithm. We find the peak height first, then work backward to find takeoff. This is much more robust than forward searching from the video start."

### Quality Metrics

"We're proud of our engineering standards: 206 automated tests ensuring reliability, full type safety with pyright for error prevention, and continuous integration that runs on every commit."

### Open Source

"And yes, it's fully open source. MIT licensed. You can audit the code, contribute improvements, or fork it for your specific needs."

______________________________________________________________________

## SLIDE 5: Jump Analysis Types (2 minutes)

### Recording Requirements

"Before we dive into the specific jump types, let me quickly mention the recording requirements. For both drop jumps and CMJs, we recommend a 45-degree camera angle - though sagittal works too - and 60+ fps video, with 30 fps as the minimum."

### Side-by-Side Comparison

"We analyze two main jump types, and they each require different approaches. Let me show you them side by side."

### Drop Jump

"On the left, drop jumps. These are all about reactive strength - how quickly can you get off the ground after landing. We measure ground contact time - fast stretch-shortening cycle is defined as less than 250 milliseconds, with trained athletes typically achieving 150-250ms. We calculate the Reactive Strength Index by dividing jump height by contact time."

"The algorithm uses forward search - we track from the drop, through ground contact, to takeoff. It's perfect for plyometric training assessment and return-to-sport testing."

### CMJ Analysis

"On the right, counter movement jumps. These start from standing and tell us about an athlete's power production. We measure jump height using the flight time method - same as force plates use - plus countermovement depth and phase durations."

"Here's the key difference: we use backward search, finding the peak first then working backward. This avoids false detections from small movements at the start. We also track triple extension - ankle, knee, hip angles - which is crucial for ACL injury prevention."

### Why Both Matter

"Different sports need different metrics. Basketball coaches care about CMJ height. Soccer coaches want to see reactive strength from drop jumps. We support both with tailored algorithms for each."

______________________________________________________________________

## SLIDE 6: Live Demo (8-10 minutes)

### Demo Setup

"Now for the fun part - let me show you this in action. I'm going to share my terminal window now - let me know if the text is too small for anyone."

\[Switch to terminal view\]

"Can everyone see the terminal clearly? Great. I have a CMJ video here from one of our test athletes."

### Demo 1: Basic Analysis

```bash
kinemotion cmj-analyze sample_data/IMG_5813.MOV
```

"Watch how quickly this processes... \[run command\] ...There! Processing takes about 3-4 times the video length, so for this 5-second video, about 15-20 seconds. And we have all metrics: jump height of 45.2cm, flight time of 606ms."

### Demo 2: Debug Visualization

"But numbers don't tell the whole story. Let me generate a debug video so you can see what the AI sees:"

```bash
kinemotion cmj-analyze sample_data/IMG_5813.MOV --output debug.mp4
```

"\[Open video\] Look at the skeleton overlay. You can see the exact moment of takeoff, how the joints extend, and the landing mechanics. This is invaluable for coaching feedback."

### Demo 3: Batch Processing

"Now imagine you recorded multiple jumps from an athlete today. Instead of analyzing one by one:"

```bash
kinemotion cmj-analyze sample_data/*.MOV --batch --workers 4
```

"All videos processing in parallel. Results exported to CSV for easy analysis in Excel or any stats software."

### Demo 4: Python Integration

"For developers in the room, here's the Python API:"

```python
from kinemotion import process_cmj_video

metrics = process_cmj_video("sample_data/IMG_5813.MOV")
print(f"Jump height: {metrics.jump_height:.3f}m")
print(f"Flight time: {metrics.flight_time * 1000:.0f}ms")
print(f"Countermovement depth: {metrics.countermovement_depth:.3f}m")
```

"Easy to integrate into existing workflows or build custom applications on top."

______________________________________________________________________

## SLIDE 7: Real-World Results (1.5 minutes)

### Engineering Quality

"We take code quality seriously. 206 automated tests ensure reliability. Every function is type-checked. Code duplication is under 3%."

### Performance Metrics

"Processing performance matters for practical use. Processing speed is about 3.5 times the video length - so a 5-second video takes around 17 seconds, a 7-second video about 25 seconds. For batch processing, 100 videos takes about 4-5 minutes with 4 parallel workers on an M1 Pro."

### Transparency

"Now, I want to be completely transparent about our validation status. We haven't yet validated against force plates - that study is planned for Q1 2025."

"What we can guarantee: consistent measurements. If athlete A jumps higher than athlete B in our system, that relationship is accurate. The absolute values might have a systematic offset we're still characterizing."

### Use Case Fit

"This makes Kinemotion perfect for tracking progress over time, comparing athletes, and identifying trends. For clinical diagnosis requiring absolute accuracy, wait for our validation study or use alongside traditional tools."

______________________________________________________________________

## SLIDE 8: Integration & Adoption (1.5 minutes)

### Getting Started

"Installing Kinemotion is as simple as `pip install kinemotion`. Works on Windows, Mac, and Linux."

### Three User Personas

"We designed for three types of users:"

"Coaches who want a simple command-line tool - just point it at your videos and get results."

"Developers who need an API - full programmatic access for custom applications."

"Researchers who need raw data - everything exports to CSV for statistical analysis."

### Documentation

"We've invested heavily in documentation. Step-by-step guides, API references, even a Spanish translation for our international users."

### Community

"Being open source, we already have contributors improving the codebase. One user added support for a new video format. Another optimized the batch processing by 30%."

______________________________________________________________________

## SLIDE 9: Technical Challenges & Lessons Learned (3 minutes)

### Technical Challenges

"Let me share some of the interesting technical challenges I've encountered in this project."

"First, pose detection. MediaPipe is amazing, but it has limitations. When an athlete's limbs occlude each other, tracking gets noisy. I spent weeks tuning filters to handle these edge cases."

"The depth estimation problem is fascinating - we're trying to extract 3D information from 2D video. The lateral or 45-degree camera angle helps, but there's still inherent ambiguity."

### Signal Processing

"The signal processing was a rabbit hole. Choosing the right Savitzky-Golay window size is critical - too small and you get noise, too large and you lose important details in fast movements."

"Sub-frame interpolation sounds simple but requires careful consideration of the underlying physics. You can't just linearly interpolate - acceleration patterns matter."

### Lessons Learned

"This project has taught me so much. Computer vision is way harder than tutorials make it seem. Real-world video has motion blur, changing lighting, different body types - every edge case you can imagine."

"The biomechanics research was eye-opening. Understanding how humans actually jump - the stretch-shortening cycle, elastic energy storage - helped me write better algorithms."

"And open source has been incredible. I've had contributors fix bugs, add features, even translate documentation to Spanish. It's amazing what happens when you put your code out there."

______________________________________________________________________

## SLIDE 10: Code Architecture Deep Dive (3 minutes)

### Architecture Overview

"Let me show you how the code is structured. This might be interesting for those thinking about extensible design patterns."

"I went with a modular architecture where each jump type is essentially a plugin. The core module handles shared functionality like pose tracking and filtering, while specific modules implement the unique algorithms."

### Design Patterns

"The key insight was using Python protocols for the analyzer interface. This gives us type safety without tight coupling. Any class that implements detect_phases and calculate_metrics can be a jump analyzer."

"Dependency injection made testing so much easier. I can swap out the video processor with a mock that returns predetermined poses. This let me write 206 tests that run in seconds rather than processing actual videos."

### Extensibility

"Want to add squat analysis? Just create a new module implementing the protocol. The CLI and API automatically pick it up. This is how we'll scale to more movements."

"Type safety with pyright has been a game-changer. It catches so many bugs before runtime. Yes, it's more work upfront, but the confidence it gives during refactoring is worth it."

______________________________________________________________________

## SLIDE 11: Future Roadmap & Q&A (2-3 minutes)

### Immediate Plans

"Next on my list is validating against actual force plates. I'm trying to get access to a university lab to run some comparison studies. If anyone has connections, let me know!"

"I'm also close to getting real-time processing working. The idea is to show metrics the instant an athlete lands - would be cool for live training feedback."

### Vision

"Eventually, I'd love to make this a mobile app. Just point your phone, record, and get instant analysis. No laptop, no command line - just results."

"I'm also thinking about other movements. Squats would be interesting - lots of people want to check their depth. Olympic lifts are complex but fascinating from a technical perspective."

### Call to Action

"So that's where I am with this project. If any of you want to try it out, play with the code, or have ideas for improvements, I'd love to collaborate. It's all on GitHub, MIT licensed, ready to fork."

### Q&A Transition

"That's my hobby project in a nutshell. I'm curious - what do you all think? Any ideas for features? Technical suggestions? Anyone else working on computer vision stuff we could combine efforts on?"

"Feel free to unmute and ask questions, or drop them in the chat - I'll make sure to address everything for the recording as well."

\[Watch both raised hands and chat for questions\]

______________________________________________________________________

## Common Q&A Responses

### Q: "How accurate is it compared to force plates?"

**A:** "Great question. We're currently conducting a validation study. Preliminary testing shows consistent relative measurements - meaning comparisons between athletes or tracking progress over time is reliable. Absolute accuracy is still being characterized. We're transparent about this in our documentation."

### Q: "What frame rate do I need?"

**A:** "We prefer 60+ fps for best results, though 30 fps is the minimum. We support up to 240 fps for high-speed cameras. The auto-tuning system adapts to your frame rate automatically. Most modern smartphones shoot at 60 fps by default, which is perfect."

### Q: "Can it analyze other movements?"

**A:** "Currently, we support drop jumps and CMJs. Squats and Olympic lifts are on our roadmap for 2025. The underlying pose tracking could theoretically analyze any movement - it's about developing the specific algorithms for each."

### Q: "How does it compare to My Jump Lab?"

**A:** "I've used My Jump Lab extensively, and while it's popular, I found it unreliable. It failed on many of my videos and often still required manual frame selection. Kinemotion aims to be truly automated - it works consistently without manual intervention. Plus, we're open source, so if something doesn't work, you can see why and even fix it."

### Q: "What about Tracker from Open Source Physics?"

**A:** "Tracker is fantastic for detailed physics analysis and education. It's incredibly powerful. But it requires manual point tracking for every frame, which takes forever. Kinemotion is designed for quick, automated athletic assessment. Different tools for different purposes - Tracker for physics education, Kinemotion for sports performance."

### Q: "Is there a web version?"

**A:** "Not yet, but it's on our roadmap. For now, it's Python-based, which means it runs on any computer. A web interface would make it even more accessible."

### Q: "How do you handle privacy/data?"

**A:** "All processing happens locally on your computer. No videos are uploaded to any server. You maintain complete control of your data. For organizations with strict privacy requirements, you can run it entirely offline."

### Q: "Can it handle multiple athletes in one video?"

**A:** "Currently, it tracks one athlete at a time. The system is designed to analyze a single subject per video. Multi-athlete tracking is technically possible with MediaPipe but would require significant algorithm changes. It's a frequently requested feature we're considering for future development."

### Q: "What about markerless motion capture systems?"

**A:** "Commercial systems like Dari or Kinatrax cost $50,000+. They're more accurate but require specific setups. Kinemotion trades some accuracy for accessibility - any smartphone, any location, no special equipment."

______________________________________________________________________

## Closing Remarks

"Thanks everyone for your time today. This has been a really fun project to work on, and I hope some of you found the technical challenges as interesting as I do."

"I'll share the recording and all the links in a follow-up email. If anyone wants to try it out or has ideas for collaboration, just reach out - I'm always happy to talk about computer vision and signal processing challenges."

"The GitHub repo is public, so feel free to fork it, play with it, break it, fix it - whatever you want. That's the beauty of open source."

"I'll stop the recording now, but happy to stick around for more informal questions if anyone has them."

\[Stop recording, then continue with informal Q&A\]

______________________________________________________________________

## Technical Troubleshooting Tips

### If demo fails

1. Have pre-recorded output ready to show
1. Explain common issues (video codec, Python environment)
1. Pivot to showing results rather than live processing

### If questioned about limitations

1. Acknowledge current constraints honestly
1. Explain the roadmap to address them
1. Focus on what it CAN do well now

### If internet fails

1. All demos work offline
1. Have local documentation copy
1. Screenshots of web resources as backup

______________________________________________________________________

## Post-Presentation Follow-up

### Send to attendees

- Link to GitHub repository
- Installation guide
- Sample videos for testing
- Your contact information
- Slide deck PDF

### Gather feedback

- What features would be most valuable?
- What concerns need addressing?
- Who wants to beta test new features?
- Potential collaboration opportunities

### Next steps

- Schedule follow-up demos for interested parties
- Create specific tutorials for requested use cases
- Connect with potential contributors
- Document FAQ from presentation questions
