// Helpers for building the dissertation with docx-js.
const fs = require("fs");
const path = require("path");
const d = require("docx");
const {
  Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell, WidthType, BorderStyle,
  ShadingType, ImageRun, PageBreak, PositionalTab, PositionalTabAlignment, PositionalTabRelativeTo,
  PositionalTabLeader, VerticalAlign, TableLayoutType,
} = d;

const FONT = "Times New Roman";
const CONTENT_W = 8666; // A4 width 11906 - left 1800 - right 1440 (DXA)
const ROOT = path.join(__dirname, "..", "..");
const T = JSON.parse(fs.readFileSync(path.join(ROOT, "results", "doc_tables.json"), "utf8"));

// registries used for the table of contents, list of tables and list of figures
const REG = { headings: [], tables: [], figures: [] };
let tableNo = {}, figNo = {};

// inline markup: **bold**, *italic*, ^sup^, ~sub~
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|\^[^^\s]{1,12}\^|~[^~\s]{1,12}~)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
    const tok = m[0];
    if (tok.startsWith("**")) out.push(...runs(tok.slice(2, -2), { ...base, bold: true }));
    else if (tok.startsWith("*")) out.push(...runs(tok.slice(1, -1), { ...base, italics: true }));
    else if (tok.startsWith("^")) out.push(new TextRun({ text: tok.slice(1, -1), superScript: true, font: FONT, ...base }));
    else out.push(new TextRun({ text: tok.slice(1, -1), subScript: true, font: FONT, ...base }));
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
  return out;
}

const BODY = { line: 360, after: 120 };
function P(text, o = {}) {
  return new Paragraph({
    children: runs(text, { size: o.size || 24, color: o.color }),
    alignment: o.align || AlignmentType.JUSTIFIED,
    spacing: { line: o.line || BODY.line, after: o.after ?? BODY.after, before: o.before || 0 },
    indent: o.indent, keepNext: o.keepNext, pageBreakBefore: o.pageBreakBefore,
  });
}
const C = (text, o = {}) => P(text, { align: AlignmentType.CENTER, ...o });

function H1(text, o = {}) {
  REG.headings.push({ level: 1, text });
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, pageBreakBefore: o.pageBreak !== false, alignment: AlignmentType.CENTER,
    spacing: { after: 240, before: 0 },
    children: [new TextRun({ text, font: FONT, size: 28, bold: true, color: "000000" })],
  });
}
function H2(text) {
  REG.headings.push({ level: 2, text });
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, keepNext: true, spacing: { before: 200, after: 120 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true, color: "000000" })],
  });
}
function H3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3, keepNext: true, spacing: { before: 160, after: 80 },
    children: [new TextRun({ text, font: FONT, size: 24, bold: true, italics: true, color: "000000" })],
  });
}

function bullets(items, o = {}) {
  return items.map((t) => new Paragraph({
    children: runs(t, { size: o.size || 24 }), numbering: { reference: "bullets", level: 0 },
    alignment: AlignmentType.JUSTIFIED, spacing: { line: o.line || 336, after: 60 },
  }));
}
function numbered(items, ref = "numbers") {
  return items.map((t) => new Paragraph({
    children: runs(t, { size: 24 }), numbering: { reference: ref, level: 0 },
    alignment: AlignmentType.JUSTIFIED, spacing: { line: 336, after: 60 },
  }));
}

function eq(text) {
  return new Paragraph({ children: runs(text, { size: 24, italics: false }), alignment: AlignmentType.CENTER,
    spacing: { line: 300, before: 60, after: 120 } });
}

function caption(kind, chapter, title) {
  const reg = kind === "Table" ? tableNo : figNo;
  reg[chapter] = (reg[chapter] || 0) + 1;
  const label = `${kind} ${chapter}.${reg[chapter]}`;
  (kind === "Table" ? REG.tables : REG.figures).push({ label, title });
  return { label, para: new Paragraph({
    keepNext: kind === "Table", spacing: { before: 120, after: 80, line: 276 }, alignment: AlignmentType.LEFT,
    children: [new TextRun({ text: `${label}: `, bold: true, font: FONT, size: 22 }),
               new TextRun({ text: title, bold: true, font: FONT, size: 22 })] }) };
}
function sourceNote(text) {
  return new Paragraph({ children: runs(text, { size: 18, italics: false, color: "333333" }),
    spacing: { before: 60, after: 200, line: 252 }, alignment: AlignmentType.LEFT });
}

const thin = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
// Academic three-rule table: rule above header, below header, and at bottom
function table(chapter, title, header, rows, widthsPct, o = {}) {
  const cap = o.noCaption ? { para: new Paragraph({ children: [] }) } : caption("Table", chapter, title);
  const total = CONTENT_W;
  const widths = widthsPct.map((w) => Math.round((w / widthsPct.reduce((a, b) => a + b, 0)) * total));
  widths[widths.length - 1] += total - widths.reduce((a, b) => a + b, 0);
  const fs = o.size || 18;
  const align = (j) => (o.alignCols && o.alignCols[j]) || (j === 0 ? AlignmentType.LEFT : (o.textCols && o.textCols.includes(j) ? AlignmentType.LEFT : AlignmentType.CENTER));
  const mkRow = (cells, isHeader, idx, isLast) => new TableRow({
    tableHeader: isHeader, cantSplit: true,
    children: cells.map((c, j) => new TableCell({
      width: { size: widths[j], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      margins: { top: 40, bottom: 40, left: 70, right: 70 },
      shading: isHeader ? { fill: "EDEDED", type: ShadingType.CLEAR, color: "auto" }
        : (o.boldRows && o.boldRows.includes(idx) ? { fill: "F5F5F5", type: ShadingType.CLEAR, color: "auto" } : undefined),
      borders: { top: isHeader ? { style: BorderStyle.SINGLE, size: 8, color: "000000" } : none,
                 bottom: isHeader ? thin : (isLast ? { style: BorderStyle.SINGLE, size: 8, color: "000000" } : { style: BorderStyle.SINGLE, size: 2, color: "D9D9D9" }),
                 left: none, right: none },
      children: [new Paragraph({ alignment: align(j), spacing: { line: 240, after: 0 },
        children: runs(String(c), { size: fs, bold: isHeader || (o.boldRows && o.boldRows.includes(idx)) }) })],
    })),
  });
  const t = new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [mkRow(header, true, -1, false), ...rows.map((r, i) => mkRow(r, false, i, i === rows.length - 1))],
  });
  const out = [cap.para, t];
  if (o.source) out.push(sourceNote(o.source)); else out.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  return out;
}

function figure(chapter, title, file, widthIn, o = {}) {
  const p = path.join(ROOT, "figures", file);
  const buf = fs.readFileSync(p);
  // read PNG size
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const wpx = widthIn * 96, hpx = Math.round(wpx * h / w);
  const cap = caption("Figure", chapter, title);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data: buf, transformation: { width: wpx, height: hpx },
        altText: { title, description: title, name: file } })] }),
    cap.para,
    sourceNote(o.source || "Source: author's calculations."),
  ];
}

const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

// dot-leader line used by the static TOC / lists
function leaderLine(text, page, indent = 0, bold = false, size = 22) {
  return new Paragraph({
    spacing: { after: 40, line: 264 }, indent: { left: indent, right: 0 },
    tabStops: [{ type: d.TabStopType.RIGHT, position: CONTENT_W, leader: "dot" }],
    children: [new TextRun({ text, font: FONT, size, bold }), new TextRun({ text: "\t" + String(page), font: FONT, size, bold })],
  });
}

module.exports = { d, T, REG, FONT, CONTENT_W, ROOT, runs, P, C, H1, H2, H3, bullets, numbered, eq, table, figure,
  pageBreak, leaderLine, sourceNote, caption };
