const { d, P, C, H1, H2, bullets, leaderLine, FONT } = require("./lib");
const { Paragraph, TextRun, AlignmentType, TabStopType } = d;

const TITLE = "Mergers & Acquisitions by Reliance Industries Limited \u2013 An Analysis of Strategic Intent and Financial Outcomes";
const NAME = "Akansh Agarwal", ROLL = "FT-25-205", BATCH = "MBA (Full-Time), Batch 2025–27";
const GUIDE = "Dr. Arnav Kumar", GDES = "Assistant Professor, Finance";
const DATE = "18/10/2026";

const big = (t, size = 28, bold = true, after = 120) => new Paragraph({ alignment: AlignmentType.CENTER,
  spacing: { after, line: 360 }, children: [new TextRun({ text: t, font: FONT, size, bold })] });
const twoCol = (l, r, bold = false) => new Paragraph({ spacing: { after: 0, line: 300 },
  tabStops: [{ type: TabStopType.RIGHT, position: 8666 }],
  children: [new TextRun({ text: l, font: FONT, size: 24, bold }), new TextRun({ text: "\t" + r, font: FONT, size: 24, bold })] });
const blank = (n = 1) => Array.from({ length: n }, () => new Paragraph({ children: [] }));

function cover() {
  return [
    ...blank(2), big("DISSERTATION STUDY", 32), ...blank(2),
    big(`“${TITLE}”`, 30, true, 240), ...blank(1),
    C("A project report submitted in partial fulfilment of the requirements for the degree of Master of Business Administration (Full-Time) from the Faculty of Management Studies (FMS), University of Delhi.", { size: 24 }),
    ...blank(5),
    twoCol("Submitted by:", "Under guidance of:", true),
    twoCol(NAME, GUIDE), twoCol(BATCH, GDES), twoCol(`Roll no: ${ROLL}`, "Faculty of Management Studies"),
    twoCol(`Date: ${DATE}`, "University of Delhi"),
  ];
}

function certificate() {
  return [
    H1("CERTIFICATE", { pageBreak: false }), ...blank(1),
    P(`Certified that the dissertation entitled “${TITLE}”, submitted by ${NAME}, ${BATCH}, Roll no. ${ROLL}, in partial fulfilment of the requirements for the degree of Master of Business Administration of the Faculty of Management Studies, University of Delhi, is a bona fide record of research carried out by the student under my supervision. All sources of data and published work used have been cited. The work has not been submitted for any other degree or diploma.`),
    ...blank(3), P(`Date: ${DATE}`, { align: AlignmentType.LEFT }), ...blank(3),
    twoCol(GUIDE, NAME), twoCol("(Project Guide)", BATCH), twoCol(GDES, `Roll no: ${ROLL}`),
    twoCol("Faculty of Management Studies", ""), twoCol("University of Delhi", ""),
  ];
}

function declaration() {
  return [
    H1("DECLARATION"), ...blank(1),
    P(`I hereby declare that this dissertation titled “${TITLE}” is my original work carried out under the guidance of ${GUIDE}, ${GDES}, Faculty of Management Studies, University of Delhi. It has not been submitted elsewhere for any degree or diploma. All sources of data and published work used have been acknowledged.`),
    P("AI tools were used to assist with collecting data from company annual reports, press releases and stock-exchange filings, with the Python-based data analysis, and with editing the text of this dissertation."),
    ...blank(3),
    P("Signature: ____________________", { align: AlignmentType.LEFT, after: 0 }),
    P(NAME, { align: AlignmentType.LEFT, after: 0 }), P(BATCH, { align: AlignmentType.LEFT, after: 0 }),
    P(`Roll no: ${ROLL}`, { align: AlignmentType.LEFT, after: 0 }), P(`Date: ${DATE}`, { align: AlignmentType.LEFT }),
  ];
}

function acknowledgement() {
  return [
    H1("ACKNOWLEDGEMENT"), ...blank(1),
    P(`I would like to express my sincere gratitude to my guide, ${GUIDE}, ${GDES}, Faculty of Management Studies, University of Delhi, for his guidance throughout this dissertation. His suggestion to examine the strategic logic of every transaction, and not only its financial result, and to study the acquired companies alongside Reliance itself, shaped the final form of this work.`),
    P("I am grateful to the faculty members of the Faculty of Management Studies, whose teaching in corporate finance, strategy and research methods gave me the foundation for this study, and to the administrative and library staff for their support."),
    P("I also thank my batchmates for their suggestions and encouragement during the months of collecting and analysing the data."),
    ...blank(2),
    P(NAME, { align: AlignmentType.LEFT, after: 0 }), P(BATCH, { align: AlignmentType.LEFT, after: 0 }),
    P(`Roll no: ${ROLL}`, { align: AlignmentType.LEFT }),
  ];
}

function abstract() {
  return [
    H1("ABSTRACT"),
    P("Between 2012 and 2026 Reliance Industries Limited (RIL) changed from a refining and petrochemicals company into a group whose digital and retail businesses now earn about half of its segment profit. This dissertation asks what role mergers and acquisitions (M&A) played in that change: why RIL acquired what it did, whether the acquisitions improved financial performance, and how investors reacted. It follows a mixed-method design. In the qualitative phase, 52 RIL press releases and twelve annual reports are analysed, and each of 30 acquisitions and strategic investments announced between 2012 and 2025 is classified by Bower's (2001) typology, Ansoff's growth matrix, relatedness and stated motive. In the quantitative phase, the financial ratios of six listed companies that RIL acquired (Network18, Den Networks, Hathway, Alok Industries, Just Dial and Sterling and Wilson) and of RIL itself are compared three years before and after each acquisition using paired t-tests and Wilcoxon signed-rank tests, and the stock-market reaction to 37 announcements is measured with a market-model event study."),
    P("Five strategic themes recur: building content and distribution around Jio, extending Reliance Retail into new categories and channels, buying technology capabilities (eleven of the 30 deals are *M&A as R&D*), consolidating distressed assets, and “borrowing” capital and partners through stake sales and joint ventures. Acquisitions were small relative to RIL (median 0.09 per cent of its market value) and equal to about 6.6 per cent of its capital expenditure. RIL's shareholders showed no significant reaction to acquisitions (CAAR of −0.39 per cent over days −1 to +1, p = 0.31). Media deals drew negative returns and stake sales to Facebook, Silver Lake and others positive ones. Target shareholders gained an average 7.5 per cent over three days and 23.6 per cent over 21 days, much of it before the announcement. After acquisition the targets' debt-equity ratio fell significantly (1.34 to 0.42, p = 0.035), but their profitability did not improve significantly. RIL's operating margin was higher after each of the six acquisition years (Wilcoxon p = 0.031), while its return on equity was not. The evidence suggests that RIL used M&A to supply capabilities and reach to businesses it built organically, rather than as a source of short-run financial gain."),
    P("**Keywords:** mergers and acquisitions, strategic intent, corporate diversification, event study, post-merger performance, business groups, Reliance Industries, India", { align: AlignmentType.LEFT }),
  ];
}

function tocBlock(pagemap) {
  const pg = (t) => (pagemap && pagemap[t]) || "00";
  const out = [H1("TABLE OF CONTENTS")];
  for (const h of pagemap.__headings) {
    if (h.text === "TABLE OF CONTENTS") continue;
    out.push(leaderLine(h.text, pg(h.text), h.level === 1 ? 0 : 360, h.level === 1, h.level === 1 ? 22 : 21));
  }
  out.push(H1("LIST OF TABLES"));
  for (const t of pagemap.__tables) out.push(leaderLine(`${t.label}: ${t.title}`, pg(t.label), 0, false, 20));
  out.push(H1("LIST OF FIGURES"));
  for (const t of pagemap.__figures) out.push(leaderLine(`${t.label}: ${t.title}`, pg(t.label), 0, false, 20));
  return out;
}

function abbreviations() {
  const rows = [
    ["AR / CAR / CAAR", "Abnormal return / cumulative abnormal return / cumulative average abnormal return"],
    ["BMP", "Boehmer–Musumeci–Poulsen standardised cross-sectional test"],
    ["BSE / NSE", "BSE Limited / National Stock Exchange of India"],
    ["D/E", "Debt-equity ratio"], ["EBIT / EBITDA", "Earnings before interest and tax / before interest, tax, depreciation and amortisation"],
    ["FY", "Fiscal year ending 31 March (FY22 = April 2021 to March 2022)"],
    ["IBC", "Insolvency and Bankruptcy Code, 2016"], ["IMT", "Independent Media Trust (RIL its sole beneficiary)"],
    ["JV", "Joint venture"], ["LOI", "Letter of intent"], ["M&A", "Mergers and acquisitions"],
    ["NCLT", "National Company Law Tribunal"], ["O2C", "Oil-to-chemicals (RIL's refining, petrochemicals and fuel-marketing segment)"],
    ["OPM / NPM", "Operating profit margin / net profit margin"],
    ["RBV", "Resource-based view of the firm"], ["RIL", "Reliance Industries Limited"],
    ["RNESL / RNEL", "Reliance New Energy Solar Limited / Reliance New Energy Limited"],
    ["ROA / ROCE / ROE", "Return on assets / on capital employed / on equity"],
    ["RRVL", "Reliance Retail Ventures Limited"], ["S&W", "Sterling and Wilson Renewable Energy Limited"],
    ["₹ crore", "Indian rupees, ten million; ₹1 lakh crore = ₹1 trillion"],
  ];
  const { table } = require("./lib");
  return [H1("LIST OF ABBREVIATIONS"),
    ...table("0", "", ["Abbreviation", "Meaning"], rows, [25, 75], { size: 20, textCols: [1], noCaption: true }).slice(1)];
}

function executiveSummary() {
  return [
    H1("EXECUTIVE SUMMARY", { pageBreak: false }),
    P("**Context.** RIL has been India's most active corporate acquirer of the last decade. Between 2012 and 2025 it announced at least 30 acquisitions and strategic investments, from Network18 and Den Networks to Just Dial, REC Solar, METRO Cash & Carry and the Viacom18–Star India joint venture with Disney. In the same period it sold minority stakes in Jio Platforms and Reliance Retail Ventures to global investors for more than ₹2 lakh crore. Over the same years, Digital Services and Retail rose from about 1 per cent of RIL's segment EBIT in FY16 to about 50 per cent in FY26."),
    P("**Objectives.** (1) To analyse the strategic intent behind RIL's M&A; (2) to evaluate pre- and post-acquisition financial performance; (3) to examine the market reaction to M&A announcements and its effect on shareholder value."),
    P("**Data and method.** A mixed-method design. The qualitative phase analyses 52 RIL press releases and twelve annual reports, and classifies every deal by mode, relatedness, Ansoff direction, Bower's (2001) M&A type and stated motive. The quantitative phase uses financial statements from Screener.in and annual reports (FY2012–FY2026). It applies paired t-tests and Wilcoxon signed-rank tests to twelve ratios for six acquired listed companies and for RIL, and a market-model event study (Nifty 50 benchmark) to 37 announcements and to the six targets' own share prices."),
    P("**Key findings.**", { after: 60 }),
    ...bullets([
      "**Strategic intent.** Five themes recur: (i) content, distribution and technology to complete the Jio digital ecosystem; (ii) new categories, brands and channels for Reliance Retail; (iii) technology capability acquired as *M&A as R&D* (11 of 30 deals), including small staged bets in new energy; (iv) opportunistic consolidation of distressed assets (Alok, Kemrock, RCom's towers, Future Group); and (v) “borrowing” capital and partners through stake sales and joint ventures. Most deals are related or concentric; the unrelated ones are concentrated in new energy.",
      "**Scale.** Acquisitions were small relative to RIL: the median deal was 0.09 per cent of RIL's market value, and announced acquisitions (₹79,280 crore, including the terminated Future Group deal) were about 6.6 per cent of capital expenditure over FY15–FY26. RIL built its new businesses mainly through organic investment and used acquisitions to fill gaps in them.",
      "**Market reaction (RIL).** The average acquisition announcement produced no significant abnormal return (CAAR −0.39 per cent over days −1 to +1, p = 0.31; robust to model choice). Media deals drew negative returns (day-0 CAAR −1.08 per cent, Patell p = 0.036), as did retail deals over the 21-day window (−4.45 per cent, Wilcoxon p = 0.005). New-energy deals were mildly positive but not significant. The strongest reactions were to inbound stake sales: Facebook (+9.1 per cent), Silver Lake (+8.9 per cent) and the Aramco letter of intent (+11.2 per cent).",
      "**Market reaction (targets).** Shareholders of the six acquired companies earned an average CAR of +7.5 per cent over days −1 to +1 (Patell p < 0.001) and +23.6 per cent over days −10 to +10 (t-test p = 0.044). All six rose before the announcement (CAAR −10 to −2 of +14.1 per cent), which points to anticipation or leakage.",
      "**Financial outcomes (targets).** After RIL took control, the targets' debt-equity ratio fell from 1.34 to 0.42 (paired t p = 0.035), but changes in margins, returns and turnover were not significant. Den and Hathway turned profitable. Just Dial returned to high margins after a dip. Sterling and Wilson and Alok Industries remained loss-making through much of the post-acquisition period.",
      "**Financial outcomes (RIL).** RIL's operating margin was higher in the three years after each of its six main acquisition years than in the three years before (15.5 to 16.6 per cent on average; Wilcoxon p = 0.031). Fixed-asset turnover fell in every case (p = 0.031), and ROE, ROCE and net margin did not change significantly. Overlapping deal windows and RIL's large organic investment make it difficult to attribute these changes to M&A.",
    ]),
    P("**Implications.** RIL's M&A record is better understood as a portfolio of *capability purchases* that support organic platforms than as stand-alone value-creating transactions. For investors, the announcement of a typical RIL acquisition carries little information about value. The decisions that moved RIL's share price were those that revealed the value of the platforms (the stake sales). For managers, the experience shows the strengths of a build–borrow–buy strategy and its integration risks: the Future Group deal failed, and the cable and media assets had to be restructured.", { before: 120 }),
  ];
}

function rationale() {
  return [
    H1("RATIONALE OF THE STUDY"),
    P("RIL is India's largest private-sector company by revenue and market value, and between 2016 and 2026 it reshaped India's telecom, retail and media industries. Studying how and why it used M&A is worthwhile for four reasons."),
    ...require("./lib").numbered([
      "**Relevance to corporate strategy.** RIL's move away from hydrocarbons is one of the largest corporate transformations in an emerging market. How a mature industrial company used acquisitions, minority stakes and joint ventures to enter consumer and technology businesses is directly relevant to Indian strategists facing similar decisions.",
      "**Relevance to investors.** RIL is the largest company in the Nifty 50, and its deals are closely followed. Whether announcements create or destroy value for RIL's and the targets' shareholders, and which kinds do, matters to minority investors in both.",
      "**A natural laboratory.** RIL's deals span media, telecom infrastructure, retail, consumer brands, deep technology and new energy, and include successes, restructurings and a failed deal. Studying one acquirer across many targets holds the acquirer's governance and financing constant, so differences in strategy and outcome are easier to see.",
      "**A gap in evidence.** Indian M&A studies generally pool many acquirers and treat deals as homogeneous. Few link the strategic intent stated for each deal to its measured financial and market outcomes, and fewer study a diversified business group from the inside.",
    ], "numbers"),
  ];
}

module.exports = { cover, certificate, declaration, acknowledgement, abstract, tocBlock, abbreviations, executiveSummary, rationale, TITLE };
