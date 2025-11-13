# **Validity of a smartphone app using artificial intelligence for** **the real time measurement of barbell velocity in the bench** **press exercise.**

### BALSALOBRE-FERNÁNDEZ, Carlos, XU, Jiaqing, JARVIS, Paul, THOMPSON, Steve <http://orcid.org/0000-0001-7674-3685>, TANNION, Kyran and BISHOP, Chris Available from Sheffield Hallam University Research Archive (SHURA) at: <https://shura.shu.ac.uk/32150/>

This document is the Accepted Version \[AM\]

**Citation:**

BALSALOBRE-FERNÁNDEZ, Carlos, XU, Jiaqing, JARVIS, Paul, THOMPSON,
Steve, TANNION, Kyran and BISHOP, Chris (2023). Validity of a smartphone app
using artificial intelligence for the real time measurement of barbell velocity in the
bench press exercise. Journal of Strength and Conditioning Research, 37 (12),
e640-e645. \[Article\]

**Copyright and re-use policy**

[See http://shura.shu.ac.uk/information.html](http://shura.shu.ac.uk/information.html)

**Sheffield Hallam University Research Archive**

[http://shura.shu.ac.uk](http://shura.shu.ac.uk/)

## 1 The validity of a smartphone app using artificial intelligence for the real 2 time measurement of barbell velocity in the bench press exercise

3

4

5 **ABSTRACT**

6 The purpose of the present study was to explore the validity and within-session reliability

7 of the newly developed My Jump Lab application (app), which uses artificial intelligence

8 techniques to monitor barbell velocity in real time. Twenty-seven sport science students

9 performed 5 repetitions at 50% and 75% of their self-reported bench press one repetition

10 maximum (1-RM) during a single testing session, while barbell velocity was concurrently

11 measured using the app (installed on an iPhone 12 Pro) and the GymAware linear position

12 transducer (LPT). A very high correlation was observed between devices at each loading

13 condition (50%1-RM: _r_ = 0.90 \[0.82, 0.97\]; 75%1-RM: _r_ = 0.92 \[0.86, 0.98\]). Results

14 showed trivial differences between the app and LPT at both 50%1-RM (g = -0.06) and

15 75%1-RM (g = -0.12). Bland-Altman analysis showed a bias estimate of -0.010 m.s \[-1 \] and

16 0.026 m.s \[-1\] for the 50% and 75%1-RM, respectively. Finally, similar levels of reliability, as

17 revealed by the coefficient of variation (CV) were observed for both devices (50%1-RM:

18 LPT = 6.52%, app = 8.17%; 75%1-RM: LPT = 12.10%, app = 13.55%). Collectively, the

19 findings of this study support the use of My Jump Lab for the measurement of real time

20 barbell velocity in the bench press exercise.

21

22 _Keywords:_ computer vision; technology; resistance training; monitoring.

23 **INTRODUCTION**

24 Measuring mean concentric velocity (MCV) during resistance exercises has been proposed

25 as a non-invasive way to objectively quantify an athlete’s response to training stressors such

26 as load and volume, and indicate the level of effort produced during strength training (22). A

27 practically perfect relationship ( _r_ ≥ 0.94) has been established between MCV and % 1-RM

28 in the bench press, back squat, and deadlift among other exercises, enabling practitioners to

29 accurately estimate 1-RM and its percentages by measuring lifting velocity (5,7,9,20,21). By

30 doing so, practitioners can utilize velocity to inform training prescriptions, test athletes,

31 provide feedback, autoregulate, and control volume (6,11,17,22). In addition, subjective (i.e.,

32 the rate of perceived exertion or the number of repetitions in reserve) parameters have been

33 shown to correlate strongly with with MCV, demonstrating the versatility of velocity-based

34 training (12). The predictive capabilities of load-velocity profiling can help practitioners to

35 prescribe training loads based on velocity metrics rather than doing direct 1-RM assessments,

36 which can be time consuming, interrupt training phases through increased neuromuscular

37 fatigue, and potentially inappropriate for certain populations (e.g., youth or novice). Thus,

38 the measurement of MCV during resistance exercises has been rapidly adopted in the strength

39 and conditioning community to monitor training load and optimize training prescription

40 (11,22).

41

42 Several technologies have been validated for the measurement of MCV, with linear position

43 transducers (LPTs) often being considered as the gold standard (19,23). The main drawback

44 of LPTs, however, is often their price point, sometimes restricting their use from practitioners

45 with limited budgets. To address this limitation, more affordable technologies (e.g., inertial

46 measurement units, lower-cost motion capture systems, or smartphone apps) have been

47 developed to measure MCV, with smartphone apps and inertial measurement units being the

48 most popular and validated options (1,19,23). Specifically, video-analysis apps such as My

49 Lift or iLoad have been proposed as valid and reliable low-cost alternatives for the

50 measurement of MCV (2,14). Nevertheless, these video-analysis apps have always been

51 restricted by their calculation method which required post-set inspection of each repetition,

52 preventing real-time feedback to the athlete. Real-time feedback is an important VBT

53 application, and has been shown to facilitate a higher inter- and intra-set mechanical output,

54 in addition to eliciting greater performance improvements (15,24,25). Implementing velocity

55 loss thresholds, autoregulating load through load manipulation, and driving intent through

56 extrinsic motivation also rely on valid and reliable real-time MCV feedback (6,16,25). Recent

57 developments in computer vision and machine learning for mobile devices, however, have

58 now made real-time tracking and feedback of MCV possible. Therefore, the purpose of this

59 study was to explore the validity of a newly developed smartphone app (My Jump Lab) which

60 uses artificial intelligence techniques for the measurement of MCV in real time.

61 **METHODS**

62 _Experimental approach to the problem_

63 For the present validation study, we aimed to compare mean concentric velocity in the bench

64 press exercise, measured by the gold standard instrument (i.e., a LPT) and a newly developed

65 iOS app. To do this, two sets of five repetitions were performed by 27 resistance trained

66 subjects in the bench press exercise at 50% and 75% of their self-reported 1-RM while MCV

67 was simultaneously monitored by an LPT (Gym Aware, Technologies, Canberra, Australia)

68 and My Jump Lab app installed on an iPhone 12 Pro running iOS 15.5 (Apple Inc., Cupertino,

69 USA). A total of 270 repetitions were registered, and data between both devices were

70 compared for validity and reliability purposes.

71

72 _Subjects_

73 Twenty-seven sport science students with a minimum of one year’s experience in the bench

74 press exercise were recruited (mean ± SD: age = 24.7 ± 4.5 years; mass = 77.2 ± 10.4 kg;

75 Bench press 1-RM = 1.0 ± 0.3 kg.kg \[-1\] ). Subjects were instructed to avoid any strenuous

76 exercise two days before the testing session, had no reported injuries during the time of

77 testing, and were informed of the risks and benefits of the study before any data collection.

78 The study protocol complied with the seventh Declaration of Helsinki for Human

79 Experimentation and was approved by the Institutional Review Board at the Autonomous

80 University of Madrid. Written informed consent was obtained from each participant before

81 the beginning of data collection.

82

83 _Procedures_

84 Subjects performed a single testing session where MCV at 50% and 75% of their self

85 reported 1-RM was simultaneously registered by an LPT and the My Jump Lab app on the

86 bench press exercise. The intention of the present study was not to test the 1-RM but to use

87 a self-reported measure to register MCV across two different submaximal loads.. Subjects

88 were instructed to report their closest 1-RM to the testing session, and they were required to

89 have performed it no more than 3 months and no less than 3 days before the testing session.

90 After a standardized 10-minute dynamic warm-up including body weight exercises (i.e.,

91 push-ups, lunges, squats, etc.) and 2 sets with an empty barbell on the bench press, subjects

92 performed two sets of five repetitions at their self-reported 50% and 75% 1-RM. Intra-set

93 repetitions were separated by 2 seconds of rest, while inter-set passive rest was set at 2

94 minutes. The bench press was performed in the usual manner, where subjects unracked the

95 barbell and were asked to hold it above their chest for 2-seconds (allow the My Jump Lab

96 app to detect the plate), and then initiated the eccentric portion of the movement under

97 control, whilst being asked to perform the concentric phase of the exercise as explosively as

98 possible.

99

100 _Instruments_

101 The validated GymAware LPT was used as the gold standard method in the present

102 investigation (13). All data collected from the LPT was transmitted via a Bluetooth

103 connection to the iPad Pro 12 (Apple Inc., USA) using GymAware Lite software (v2.10,

104 Kinetic Performance Technology, Canberra, Australia). An updated version of the previously

105 validated _My Lift_ iOS app (2), rebranded under the name _My Jump Lab_ was used to explore

106 its validity and reliability. The updated My Jump Lab v. 3.0 for iOS was installed on an

107 iPhone 12 Pro running iOS 15.5 (Apple Inc., Cupertino, USA). The appmeasured MCV in

108 real time by performing an object recognition request using an ad-hoc machine learning

109 model. Specifically, an object detection network based on YOLOv2 architecture was trained

110 using the free CreateML software (Apple Inc., Cupertino, USA) and a set of 1000 images of

111 weightlifting plates of different manufacturers and colors. Images included bumper plates,

112 iron plates and standard weightlifting plates; however, only completely circular and standard

113 size plates (i.e., 0.45 m of diameter) were used. The model was then integrated into the app

114 by using Apple’s open-source Swift 5 programming language and Xcode 13.4.1 for macOS

115 (Apple Inc., Cupertino, USA). Live object recognition features were included using Apple’s

116 computer-vision framework “Vision” (Apple Inc., Cupertino, USA). Specific, technical

117 details of this framework can be found following this link:

118 [https://developer.apple.com/documentation/vision. Finally, MCV of each repetition was](https://developer.apple.com/documentation/vision)

119 calculated by the object recognition algorithm.

120

121 To register MCV from the app, the iPhone was mounted to a camera tripod to record the

122 sagittal plane of the participants, at a height such that the focal center of the video screen

123 passed approximately 1.2 m above the floor with the barbell centered horizontally on the

124 screen. The positioning of the tripod from the participant was determined from pilot testing

125 and was chosen such that the full bench movement could be recorded, without the plate going

126 of the screen while the tripod was as close to the participant as possible. Data from the app

127 was collected at 60Hz.

128

129 _Statistical analyses_

130 All values were initially recorded as means ± SD in Microsoft Excel. Normality of the data

131 was confirmed using the Kolmogorov Smirnov test ( _p_ - 0.05). Within-session reliability was

132 computed for both measurement methods using the coefficient of variation (CV) with 95%

133 confidence intervals (CI), calculated as: (SD/average)\*100 and a two-way random intraclass

134 correlation coefficient (ICC 2,1) with absolute agreement and 95% CI. CV values less than

135 10% were deemed acceptable (4) and guidelines from (10) were used to interpret ICC values,

136 where: > 0.90 = excellent, 0.75-0.90 = good, 0.50-0.74 = moderate, and \< 0.50 = poor. Limits

137 of agreement (LOA) and 95% CI between the LPT and the My Jump Lab app were

138 determined from Bland-Altman plots (3). In order to determine concurrent validity between

139 measurement methods, Pearson’s correlation coefficients ( _r_ ) were calculated. Systematic

140 bias between methods was determined by paired samples _t_ -tests for each load, with statistical

141 significance set at _p_ \< 0.05. Finally, practical significance between the LPT and My Jump

142 Lab app was also determined using Cohen's _d_ with a Hedges _g_ correction effect sizes with

143 95% CI. These were interpreted in line with suggestions by Rhea (2004) relative to the

144 “recreationally trained” sample in the present study: \< 0.35 = trivial, 0.35-0.79 = small, 0.80

145 1.49 = moderate and > 1.50 = large. The statistical software Jamovi 2.3.21 for macOS was

146 used.

147 **RESULTS**

148 All data were normally distributed ( _p_ - 0.05). Table 1 and Table 2 show reliability statistics

149 and mean ± SD data for the LPT and the app, respectively. Both methods showed acceptable

150 CV values for 50% load (LPT = 6.52%, app = 8.17%). However, both measurement methods

151 exhibited greater variability for the 75% load (LPT = 12.10%, app = 13.55%), which

152 consequently had impacted reliability of the pooled data when using the app (10.86%). The

153 ICC values were excellent for 50% and 70% of maximum loads using LPT (0.96-0.98) and

154 app (0.96-0.97). When assessing systematic bias between measurement methods, no

155 significant differences were evident across either load (table 2). Specifically, differences

156 between the LPT and app were _trivial_ at 50% load ( _g_ = -0.06), _trivial_ at 75% load ( _g_ = -0.12),

157 and _trivial_ when data was pooled ( _g_ = -0.14).

158

159 _\*\* Insert Table 1-2 about here \*\*_

160

161 Figures 1 and 2 show scatter plot graphs presenting all trials for 50% and 75% of maximum

162 load, respectively, with correction equations and _r_ \[2\] values. Pearson’s _r_ values were as follows:

163 50% load (0.90 \[0.82, 0.97\]) and 75% (0.92 \[0.86, 0.98\]). Figures 3 and 4 show Bland

164 Altman plots for 50% load and 75% load, respectively. Mean differences (bias estimate) for

165 50% load concentric velocity were -0.010 m.s \[-1\] (95%CI: -0.024, 0.003 m.s \[-1\] ), indicating

166 perfect levels of agreement between two methods. Almost perfect levels of agreement were

167 also evidence between LPT and the app when the bias estimate was applied to 75% load

168 concentric velocity (-0.026 m.s \[-1\] ; 95%CI: -0.038, -0.014 m.s \[-1\] ). Coefficients of determination

169 of the regression line in the Bland-Altman plots were R \[2\] = 0.01 and R \[2\] = 0.08 for 50% and

170 75% load, respectively.

171

172 _\*\* Insert Figures 1-4 about here \*\*_

173 **Discussion**

174 The aims of the present study were to: 1) determine the validity of the My Jump Lab

175 smartphone app for measuring MCV in real time during the bench press exercise across 50%

176 and 75% 1RM, and 2) determine the within-session reliability of the My Jump Lab app within

177 these loads. From a validity standpoint, the My Jump Lab app showed a near perfect

178 correlation with an LPT for the measurement of MCV across different loads ( _r_ - 0.920; _r_ _\[2\]_ =

179 0.803). The reliability were excellent for both loads across the LPT (ICC = 0.97-0.98) and

180 app (ICC = 0.96), but with the slightly elevated CV values for the 75% loading condition in

181 both the LPT (CV = 12.10%) and the app (CV = 13.55%).

182

183 My Jump Lab uses a machine learning model that has been ‘trained’ to detect the coordinates

184 of a weight plate during live video feed. This information is then used to calibrate pixels and

185 convert to distance travelled, as an initial form of analysis. The app then calculates the time

186 taken for that distance to be travelled, which subsequently enables the calculation of mean

187 velocity (i.e., distance/time). Figure 1 and 2 show the near perfect correlation between the

188 two technologies, and practitioners can now confidently measure MCV during the bench

189 press exercise using the My Jump Lab smartphone app, in real time. This is further supported

190 by the Bland-Altman analysis (Figure 3 and 4), which shows mean bias estimates of -0.010

191 \[lower -0.168 and upper 0.147 limits of agreement\] at 50% self-reported loads and -0.026

192 \[lower -0.166 and upper 0.114 limits of agreement\] at 75%, indicating excellent levels of

193 agreement between the two technologies. LPT’s can cost a minimum of $400, often

194 outpricing practitioners and limiting their use within practice (18). In contrast, the My Jump

195 Lab app can be installed on any mobile device running iOS 13 or higher at a substantially

196 more affordable cost ($4.99 per month or $84.99 for a lifetime license), which can be used

197 as a valid alternative to the gold standard LPT. In addition, monitoring velocity is now

198 considered an integral aspect of autoregulation, enabling practitioners to monitor acute

199 fatigue and subsequently adapt training programs in real time, if required (8).

200

201 The My Jump Lab app, also exhibits excellent within-session reliability (ICC ≥ 0.96) when

202 measuring MCV across two different loads (50% and 75% 1RM, Table 1), while the CV

203 values were very similar for both technologies across all measured loads (table 1).

204 Nevertheless, it should be acknowledged that when increasing to 75% of the maximum load,

205 the measured MCV exhibits a larger amount of within-session variability, regardless of

206 whether practitioners use an LPT (CV = 12.10%) or the My Jump Lab app (CV = 13.55%).

207 Whilst this data suggests that reliability is worse at greater loads (i.e., CV > 10% threshold),

208 it is our suggestion that participants showed greater trial-to-trial variation at 75%, because

209 the load was ‘heavy enough’ to exhibit some level of acute fatigue by the fifth repetition,

210 consequently impacting the consistency of MCV (as measured by the CV). In addition, we

211 also quantified differences in MCV between technologies (Table 2). A notable trend in the

212 data was the over-estimation of velocity for the My Jump Lab app, which is likely down to

213 the conversion from pixels to distance travelled. Simply put, the app slightly under-estimates

214 the diameter of the weight plate, which results in a slight over-estimation of the distance data

215 that is reported. Furthermore, given how velocity is then calculated, this has a knock-on effect

216 in reporting higher MCV values. When considering the effects of this across two devices,

217 only trivial differences in MCV have been found under 50% ( _g_ = -0.06) and 75% ( _g_ = -0.12)

218 loading conditions. Consequently, it appears that the My Jump Lab app is a valid and reliable

219 tool to measure the MCV during the bench press. While previous research relating to the

220 validity of existing technologies to monitor barbell velocity have used different loads and

221 instruments (24), results in our study suggest that the coefficient of determination of My

222 Jump Lab in comparison with the criterion are slightly smaller than those obtained with linear

223 transducers, and slightly higher than those obtained with inertial measurement units.

224

225 A few limitations of the present study should be acknowledged. Firstly, the present study

226 employed a single testing session for the purpose of validating the My Jump Lab app. Future

227 studies may wish to consider a test-retest design, which will provide true day-to-day

228 consistency and reliability data for My Jump Lab. Secondly, future research should also aim

229 to quantify the validity and reliability of the My Jump Lab app in lower body exercises (e.g.,

230 back squat and deadlift). Given the prevalence of these exercises in athlete training

231 programmes, this would be a useful addition to the research conducted using smartphone

232 technologies. Thirdly, we recruited sport science students as subjects and future studies

233 should also consider the use of elite athlete populations when using the My Jump Lab app,

234 as their increased training age are likely to result in different raw MCV values, which in turn,

235 may also impact the subsequent reliability data as well. Fourthly, the app was trained with

236 images of circular, 0.45 m diameter plates, so it shouldn’t be used with smaller plates or

237 plates that are not circular in shape. However, future studies may wish to to explore the ability

238 of the app to measure movement velocity with such non-standard equipment, enabling an

239 even wider reach to practitioners. Finally, the data from this study only pertains to two loads

240 out the LVP spectrum. We decided to use 50% and 75% loads in order to cover a wide enough

241 range of velocities, enabling us to test the accuracy of the app with fast to slow repetitions.

242 Velocities in our data ranged from 1.24 to 0.17 m/s, with an average velocity of 0.80 m/s and

243 0.55 m/s for 50% and 75% 1-RM, respectively. Thus, with those two selected loads, we were

244 able to test a range of velocities. Better understanding how the reliability and validity changes

245 across a full LVP could be useful information for S&C coaches to know.

246

247 In conclusion, the findings of this study indicate that the My Jump Lab app can provide the

248 reliable and almost identical MCV data to that of the LPT when using 50% of the maximum

249 load. Furthermore, the app may well be usable at heavier loads (i.e., 75%), seeing as

250 reliability data was comparable with the LPT. However, as previously mentioned, further

251 research is needed to more accurately determine the day-to-day variability of MCV using the

252 My Jump Lab app, especially using heavier loads (i.e., ≥ 75%).

253

254 **Practical Applications**

255 Results in our study showed that a smartphone app using artificial intelligence is able to

256 monitor barbell velocity in the bench press exercise with a range of velocities in a valid and

257 reliable way, in comparison with a professional linear transducer. Moreover, no markers on

258 the barbell are needed, and the app works without previous calibration other than placing the

259 phone on a tripod and recording the athlete in the sagittal plane. Considering how valuable

260 velocity-based training can be for the strength and conditioning community, results in our

261 study could be of interest to athletes, sport scientists, or coaches who wish to monitor barbell

262 velocity during the bench press exercise without the need for expensive equipment.

263

264 **Conflicts of Interest Statement**

265 The first author of the present investigation is the developer of the app mentioned. To

266 guarantee data independency, data were collected and analyzed by independent researchers

267 not related with the app’s development (specifically, the second, third and last authors of the

268 present manuscript). Raw data is available at shorturl.at/clwMV.

269 **References**

270 1. Balsalobre-Fernández, C, Marchante, D, Baz-Valle, E, Alonso-Molero, I, Jiménez,

271 SL, and Muñóz-López, M. Analysis of wearable and smartphone-based technologies

272 for the measurement of barbell velocity in different resistance training exercises.

273 _Front Physiol_ 28: 649–658, 2017.

274 2. Balsalobre-Fernández, C, Marchante, D, Muñoz-López, M, and Jiménez, SL.

275 Validity and reliability of a novel iPhone app for the measurement of barbell velocity

276 and 1RM on the bench-press exercise. _J Sports Sci_ 36: 64–70, 2018.Available from:

277 <https://www.tandfonline.com/doi/full/10.1080/02640414.2017.1280610>

278 3. Bland, JM and Altman, DG. Comparing two methods of clinical measurement: A

279 personal history. _Int J Epidemiol_ 24: 7–14, 1995.

280 4. Cormack, SJ, Newton, RU, McGuigan, MR, and Cormie, P. Neuromuscular and

281 Endocrine Responses of Elite Players During an Australian Rules Football Season.

282 _Int J Sport Physiol Perform_ 3: 439–453, 2008.Available from:

283 <http://search.ebscohost.com/login.aspx?direct=true&AuthType=ip,cookie,url,uid&db>

284 =sph&AN=35883051&lang=es&site=ehost-live

285 5. Dorrell, HF, Moore, JM, Smith, MF, and Gee, TI. Validity and reliability of a linear

286 positional transducer across commonly practised resistance training exercises. _J_

287 _Sports Sci_ 37: 67–73, 2019.

288 6. Dorrell, HF, Smith, MF, and Gee, TI. Comparison of velocity-based and traditional

289 percentage-based loading methods on maximal strength and power adaptations. _J_

290 _Strength Cond Res_ 34: 46–53, 2020.

291 7. García-Ramos, A, Suzovic, D, and Pérez-Castilla, A. The load-velocity profiles of

292 three upper-body pushing exercises in men and women. _Sport Biomech_ 20: 693–705,

293 2021.

294 8. Greig, L, Hemingway, BHS, Aspe, RR, Cooper, K, Comfort, P, and Swinton, PA.

295 Autoregulation in Resistance Training: Addressing the Inconsistencies. Sport. Med.

296 50: 1873–1887, 2020.

297 9. Janicijevic, D, Jukic, I, Weakley, J, and Garcia-Ramos, A. Bench press one

298 repetition maximum estimation through the individualised load-velocity relationship:

299 comparison of different regression models and minimal velocity thresholds. _Int J_

300 _Sports Physiol Perform_ Ahead of p, 2021.

301 10. Koo, TK and Li, MY. A Guideline of Selecting and Reporting Intraclass Correlation

302 Coefficients for Reliability Research. _J Chiropr Med_ 15: 155–163, 2016.Available

303 from: <http://linkinghub.elsevier.com/retrieve/pii/S1556370716000158>

304 11. Mann, BJ, Ivey, PA, and Sayers, SP. Velocity-based training in football. _Strength_

305 _Cond J_ 37: 52–57, 2015.

306 12. Odgers, JB, Zourdos, MC, Helms, ER, Candow, DG, Dahlstrom, B, Bruno, P, et al.

307 Rating of perceived exertion and velocity relationships among trained males and

308 females in the front squat and hexagonal bar deadlift. _J Strength Cond Res_ 35: S23–

309 S30, 2021.

310 13. Orange, ST, Metcalfe, JW, Liefeith, A, Marshall, P, Madden, LA, Fewster, CR, et al.

311 Validity and reliability of a wearable inertial sensor to measure velocity and power

312 in the back squat and bench press. _J strength Cond Res_ 33: 2398–2408, 2019.

313 14. Pérez-Castilla, A, Boullosa, D, and García-Ramos, A. Reliability and validity of the

314 iLOAD application for monitoring the mean set velocity during the back squat and

315 bench press exercises performed against different loads. _J Strength Cond Res_ 35:

316 S57–S65, 2021.

317 15. Randell, AD, Cronin, JB, Keogh, JWL, Gill, ND, and Pedersen, MC. Effect of

318 Instantaneous Performance Feedback During 6 Weeks of Velocity-Based Resistance

319 Training on Sport-Specific Performance Tests. _J Strength Cond Res_ 25: 87–93,

320 2011.

321 16. Riscart-López, J, Rendeiro-Pinho, G, Mil-Homens, P, Soares-daCosta, R, Loturco, I,

322 Pareja-Blanco, F, et al. Effects of four different velocity-based training programming

323 models on strength gains and physical performance. _J Strength Cond Res_ 35: 596–

324 603, 2021.

325 17. Sánchez-Medina, L and González-Badillo, JJ. Velocity loss as an indicator of

326 neuromuscular fatigue during resistance training. _Med Sci Sports Exerc_ 43: 1725–

327 1734, 2011.

328 18. Thompson, SW, Olusoga, P, Rogerson, D, Ruddock, A, and Barnes, A. “Is it a slow

329 day or a go day?”: The perceptions and applications of velocity-based training within

330 elite strength and conditioning. _Int J Sport Sci Coach_ Published, 2022.

331 19. Thompson, SW, Rogerson, D, Dorrell, HF, Ruddock, A, and Barnes, A. The

332 Reliability and Validity of Current Technologies for Measuring Barbell Velocity in

333 the Free-Weight Back Squat and Power Clean. _Sports_ 8: 94, 2020.Available from:

334 \<www.mdpi.com/journal/sportsArticle>

335 20. Thompson, SW, Rogerson, D, Ruddock, A, Banyard, HG, and Barnes, A. Pooled

336 Versus Individualized Load–Velocity Profiling in the Free-Weight Back Squat and

337 Power Clean. _Int J Sports Physiol Perform_ 1–9, 2020.Available from:

338 <https://pubmed.ncbi.nlm.nih.gov/33547259/>

339 21. Thompson, SW, Rogerson, D, Ruddock, A, Greig, L, Dorrell, HF, and Barnes, A. A

340 novel approach to 1RM prediction using the load-velocity profile: A comparison of

341 models. _Sports_ 9: 88–99, 2021.

342 22. Weakley, J, Mann, B, Banyard, H, McLaren, S, Scott, T, and Garcia-Ramos, A.

343 Velocity-Based Training: From theory to application. _Strength Cond J_ Publish Ah,

344 2020.Available from: <https://www.researchgate.net/publication/341554144>

345 23. Weakley, J, Morrison, M, García-Ramos, A, Johnston, R, James, L, and Cole, MH.

346 The Validity and Reliability of Commercially Available Resistance Training

347 Monitoring Devices: A Systematic Review. _Sport Med_, 2021.Available from:

348 <http://link.springer.com/10.1007/s40279-020-01382-w>

349 24. Weakley, J, Till, K, Sampson, J, Banyard, H, Leduc, C, Wilson, K, et al. The effects

350 of augmented feedback on sprint, jump, and strength adaptations in rugby union

351 players after a 4-week training program. _Int J Sports Physiol Perform_ 14: 1205–

352 1211, 2019.

353 25. Weakley, J, Wilson, KM, Till, K, Read, DB, Darrall-Jones, J, Roe, GAB, et al.

354 Visual feedback attenuates mean concentric barbell velocity loss and improves

355 motivation, competitiveness, and perceived workload in male adolescent athletes. _J_

356 _Strength Cond Res_ 33: 2420–2425, 2019.

357 **FIGURE LEGENDS**

358 **Figure 1.** Linear regression for mean velocity between the two measurement methods during

359 50% of maximum load, inclusive of correction factor equation and R \[2\] .

360

361 **Figure 2.** Linear regression for mean velocity between the two measurement methods during

362 75% of maximum load, inclusive of correction factor equation and R \[2\] .

363

364 **Figure 3.** Bland-Altman plot showing levels of agreement between measurement methods

365 for mean velocity during 50% of maximum load, including mean bias estimate (-0.010) and

366 both lower (-0.168) and upper (0.147) limits of agreement.

367

368 **Figure 4.** Bland-Altman plot showing levels of agreement between measurement methods

369 for mean velocity during 75% of maximum load, including mean bias estimate (-0.026) and

370 both lower (-0.166) and upper (0.114) limits of agreement.
