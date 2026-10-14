// Build the dissertation .docx. Usage: node build.js [pagemap.json]
const fs = require("fs");
const path = require("path");
const L = require("./lib");
const { d, REG, FONT } = L;
const { Document, Packer, Paragraph, TextRun, AlignmentType, Footer, PageNumber, NumberFormat, LevelFormat } = d;
const F = require("./front");

const pagemapFile = process.argv[2];
const pm = pagemapFile && fs.existsSync(pagemapFile) ? JSON.parse(fs.readFileSync(pagemapFile, "utf8")) : {};

// 1) content in document order; TOC is inserted afterwards
const front1 = [...F.certificate(), ...F.declaration(), ...F.acknowledgement(), ...F.abstract()];
REG.headings.push({ level: 0, text: "__TOC__" });
const front2 = F.abbreviations();
const main = [
  ...F.executiveSummary(), ...F.rationale(), ...require("./ch1")(), ...require("./ch2")(), ...require("./ch3")(),
  ...require("./ch4a")(), ...require("./ch4b")(), ...require("./ch5")(),
  ...require("./back").bibliography(), ...require("./back").appendices(),
];
// first heading of each section should not force an extra page break
const snapshot = { headings: REG.headings.slice(), tables: REG.tables.slice(), figures: REG.figures.slice() };
const tocHeads = [];
for (const h of snapshot.headings) {
  if (h.text === "__TOC__") { tocHeads.push({ level: 1, text: "LIST OF TABLES" }, { level: 1, text: "LIST OF FIGURES" }); continue; }
  tocHeads.push(h);
}
pm.__headings = tocHeads; pm.__tables = snapshot.tables; pm.__figures = snapshot.figures;
const toc = F.tocBlock(pm);
fs.writeFileSync(path.join(__dirname, "registry.json"), JSON.stringify(
  { headings: tocHeads, tables: snapshot.tables, figures: snapshot.figures }, null, 1));

const footer = (fmt) => new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
  new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 }),
  new TextRun({ text: " | P a g e", font: FONT, size: 20, color: "7F7F7F" })] })] });

const page = { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1300, left: 1800, right: 1440, footer: 600 } };
const numberedRef = (ref) => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
  alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 567, hanging: 397 } } } }] });

const doc = new Document({
  creator: "Akansh Agarwal", title: F.TITLE, description: "MBA dissertation, FMS, University of Delhi",
  styles: { default: { document: { run: { font: FONT, size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: FONT }, paragraph: { spacing: { after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: FONT }, paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, italics: true, font: FONT }, paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 } },
    ] },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 567, hanging: 340 } } } }] },
    ...["numbers", "objectives", "criteria", "theory", "recs"].map(numberedRef),
  ] },
  sections: [
    { properties: { page }, children: F.cover() },
    { properties: { page: { ...page, pageNumbers: { start: 2, formatType: NumberFormat.LOWER_ROMAN } } },
      footers: { default: footer() }, children: [...front1, ...toc, ...front2] },
    { properties: { page: { ...page, pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } },
      footers: { default: footer() }, children: main },
  ],
});
const out = path.join(__dirname, "..", "Akansh_Agarwal_RIL_MA_Dissertation_Draft.docx");
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(out, b); console.log("wrote", out, b.length); });
