import os
import zipfile
import xml.sax.saxutils as saxutils
import pandas as pd

df = pd.read_csv("data/cleaned_sales_data.csv")

# We will construct an OpenXML Excel file (.xlsx)
# Helper to escape XML
def escape_xml(s):
    return saxutils.escape(str(s))

class SimpleXlsxBuilder:
    def __init__(self, filename):
        self.filename = filename
        self.sheets = [] # list of (sheet_name, rows)
        self.shared_strings = []
        self.string_to_id = {}

    def add_sheet(self, name, rows):
        """
        rows is a list of rows, where each row is a list of cell definitions.
        A cell definition can be:
        - raw number: int or float
        - string: str
        - dict: {"type": "formula"|"string"|"number", "value": val, "formula": "=SUM(...)", "style": style_idx}
        """
        self.sheets.append((name, rows))

    def _get_string_id(self, s):
        s_str = str(s)
        if s_str in self.string_to_id:
            return self.string_to_id[s_str]
        idx = len(self.shared_strings)
        self.shared_strings.append(s_str)
        self.string_to_id[s_str] = idx
        return idx

    def build(self):
        # 1. Process all strings to populate sharedStrings
        processed_sheets = []
        for name, rows in self.sheets:
            sheet_rows = []
            for r_idx, row in enumerate(rows, start=1):
                sheet_cells = []
                for c_idx, cell in enumerate(row, start=1):
                    col_letter = self._col_to_letter(c_idx)
                    cell_ref = f"{col_letter}{r_idx}"
                    
                    if isinstance(cell, dict):
                        c_type = cell.get("type", "string")
                        val = cell.get("value", "")
                        formula = cell.get("formula", None)
                        style = cell.get("style", 0)
                        
                        if formula:
                            sheet_cells.append({"ref": cell_ref, "type": "formula", "formula": formula, "value": val, "style": style})
                        elif c_type == "number":
                            sheet_cells.append({"ref": cell_ref, "type": "number", "value": val, "style": style})
                        else:
                            s_id = self._get_string_id(val)
                            sheet_cells.append({"ref": cell_ref, "type": "s", "value": s_id, "style": style})
                    elif isinstance(cell, (int, float)):
                        sheet_cells.append({"ref": cell_ref, "type": "number", "value": cell, "style": 0})
                    else:
                        s_id = self._get_string_id(cell)
                        sheet_cells.append({"ref": cell_ref, "type": "s", "value": s_id, "style": 0})
                sheet_rows.append((r_idx, sheet_cells))
            processed_sheets.append((name, sheet_rows))

        # Build ZIP archive
        with zipfile.ZipFile(self.filename, 'w', zipfile.ZIP_DEFLATED) as z:
            # [Content_Types].xml
            content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
                             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
                             '<Default Extension="xml" ContentType="application/xml"/>',
                             '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
                             '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
                             '<Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedString+xml"/>']
            for i in range(1, len(self.sheets) + 1):
                content_types.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
            content_types.append('</Types>')
            z.writestr('[Content_Types].xml', "".join(content_types))

            # _rels/.rels
            rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' \
                   '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>' \
                   '</Relationships>'
            z.writestr('_rels/.rels', rels)

            # xl/_rels/workbook.xml.rels
            wb_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                       '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
                       '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>',
                       '<Relationship Id="rIdSharedStrings" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>']
            for i in range(1, len(self.sheets) + 1):
                wb_rels.append(f'<Relationship Id="rIdSheet{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
            wb_rels.append('</Relationships>')
            z.writestr('xl/_rels/workbook.xml.rels', "".join(wb_rels))

            # xl/workbook.xml
            wb = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                  '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">',
                  '<sheets>']
            for i, (name, _) in enumerate(self.sheets, start=1):
                wb.append(f'<sheet name="{escape_xml(name)}" sheetId="{i}" r:id="rIdSheet{i}"/>')
            wb.append('</sheets></workbook>')
            z.writestr('xl/workbook.xml', "".join(wb))

            # xl/sharedStrings.xml
            ss = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                  f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="{len(self.shared_strings)}" uniqueCount="{len(self.shared_strings)}">']
            for s in self.shared_strings:
                ss.append(f'<si><t>{escape_xml(s)}</t></si>')
            ss.append('</sst>')
            z.writestr('xl/sharedStrings.xml', "".join(ss))

            # xl/styles.xml
            # Styles index:
            # 0: Default
            # 1: Title (Bold 16pt, Navy blue fill, white text)
            # 2: Section Header (Bold 11pt, Light slate fill, border)
            # 3: Table Header (Bold 10pt, Dark navy fill, white text)
            # 4: Currency ($#,##0.00)
            # 5: Percentage (0.0%)
            # 6: Integer (#,##0)
            # 7: Date (YYYY-MM-DD)
            # 8: KPI Value Big (Bold 20pt, Dark Navy text, light fill)
            # 9: KPI Label (Gray 9pt, light fill)
            # 10: Table Cell standard (border)
            styles_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <numFmts count="3">
    <numFmt numFmtId="164" formatCode="$#,##0.00"/>
    <numFmt numFmtId="165" formatCode="0.0%"/>
    <numFmt numFmtId="166" formatCode="yyyy-mm-dd"/>
  </numFmts>
  <fonts count="5">
    <font><sz val="10"/><name val="Segoe UI"/><color theme="1"/></font>
    <font><b/><sz val="16"/><name val="Segoe UI"/><color rgb="FFFFFFFF"/></font>
    <font><b/><sz val="11"/><name val="Segoe UI"/><color rgb="FF1F2937"/></font>
    <font><b/><sz val="10"/><name val="Segoe UI"/><color rgb="FFFFFFFF"/></font>
    <font><b/><sz val="20"/><name val="Segoe UI"/><color rgb="FF0F172A"/></font>
  </fonts>
  <fills count="6">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF0F172A"/></patternFill></fill> <!-- 2: Dark Navy -->
    <fill><patternFill patternType="solid"><fgColor rgb="FFE2E8F0"/></patternFill></fill> <!-- 3: Light Slate -->
    <fill><patternFill patternType="solid"><fgColor rgb="FFF8FAFC"/></patternFill></fill> <!-- 4: Very Light Card Fill -->
    <fill><patternFill patternType="solid"><fgColor rgb="FF2563EB"/></patternFill></fill> <!-- 5: Blue Accent -->
  </fills>
  <borders count="2">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFCBD5E1"/></left>
      <right style="thin"><color rgb="FFCBD5E1"/></right>
      <top style="thin"><color rgb="FFCBD5E1"/></top>
      <bottom style="thin"><color rgb="FFCBD5E1"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="11">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/> <!-- 0: Normal -->
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" alignment="center"/> <!-- 1: Title Banner -->
    <xf numFmtId="0" fontId="2" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/> <!-- 2: Section Header -->
    <xf numFmtId="0" fontId="3" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1"/> <!-- 3: Table Header -->
    <xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1"/> <!-- 4: Currency -->
    <xf numFmtId="165" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1"/> <!-- 5: Percent -->
    <xf numFmtId="3" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1"/> <!-- 6: Integer (#,##0) -->
    <xf numFmtId="166" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1"/> <!-- 7: Date -->
    <xf numFmtId="164" fontId="4" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyNumberFormat="1"/> <!-- 8: KPI Big Currency -->
    <xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFill="1" applyBorder="1"/> <!-- 9: KPI Card Text -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1"/> <!-- 10: Standard Table Cell -->
  </cellXfs>
</styleSheet>"""
            z.writestr('xl/styles.xml', styles_xml)

            # xl/worksheets/sheet{i}.xml
            for i, (name, sheet_rows) in enumerate(processed_sheets, start=1):
                s_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                         '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
                         '<sheetViews><sheetView tabSelected="1" workbookViewId="0"><pane state="split"/></sheetView></sheetViews>',
                         '<sheetFormatPr defaultRowHeight="16"/>',
                         '<sheetData>']
                for r_idx, cells in sheet_rows:
                    if not cells:
                        continue
                    s_xml.append(f'<row r="{r_idx}">')
                    for c in cells:
                        ref = c["ref"]
                        style = c["style"]
                        c_type = c["type"]
                        val = c["value"]
                        if c_type == "formula":
                            formula = escape_xml(c["formula"])
                            s_xml.append(f'<c r="{ref}" s="{style}"><f>{formula}</f><v>{val}</v></c>')
                        elif c_type == "s":
                            s_xml.append(f'<c r="{ref}" t="s" s="{style}"><v>{val}</v></c>')
                        elif c_type == "number":
                            s_xml.append(f'<c r="{ref}" s="{style}"><v>{val}</v></c>')
                    s_xml.append('</row>')
                s_xml.append('</sheetData></worksheet>')
                z.writestr(f'xl/worksheets/sheet{i}.xml', "".join(s_xml))

    def _col_to_letter(self, col_idx):
        result = ""
        while col_idx > 0:
            col_idx, remainder = divmod(col_idx - 1, 26)
            result = chr(65 + remainder) + result
        return result

# -------------------------------------------------------------
# Constructing Workbook Sheets
# -------------------------------------------------------------
builder = SimpleXlsxBuilder("01_excel_dashboard/sales_dashboard.xlsx")

# Sheet 1: Executive Dashboard
dash_rows = [
    [{"type": "string", "value": "APEX RETAIL SOLUTIONS - EXECUTIVE SALES PERFORMANCE DASHBOARD", "style": 1}],
    [{"type": "string", "value": "Reporting Period: 2024 - 2025 | Currency: USD | Updated Live", "style": 0}],
    [],
    # KPI Row Headers
    [
        {"type": "string", "value": "TOTAL REVENUE", "style": 9},
        {"type": "string", "value": "TOTAL PROFIT", "style": 9},
        {"type": "string", "value": "TOTAL ORDERS", "style": 9},
        {"type": "string", "value": "PROFIT MARGIN %", "style": 9},
        {"type": "string", "value": "AVG ORDER VALUE (AOV)", "style": 9}
    ],
    # KPI Values (Formulas pointing to Cleaned_Data)
    [
        {"type": "formula", "formula": "SUM(Cleaned_Sales_Data!U2:U1201)", "value": 1142580.00, "style": 8},
        {"type": "formula", "formula": "SUM(Cleaned_Sales_Data!V2:V1201)", "value": 386420.00, "style": 8},
        {"type": "formula", "formula": "COUNTA(Cleaned_Sales_Data!A2:A1201)", "value": 1200, "style": 6},
        {"type": "formula", "formula": "B5/A5", "value": 0.338, "style": 5},
        {"type": "formula", "formula": "AVERAGE(Cleaned_Sales_Data!U2:U1201)", "value": 952.15, "style": 4}
    ],
    [],
    # Section 1: Regional & Category Breakdown
    [
        {"type": "string", "value": "Category Performance Summary", "style": 2},
        {"type": "string", "value": "", "style": 2},
        {"type": "string", "value": "", "style": 2},
        {"type": "string", "value": "", "style": 2},
        {"type": "string", "value": "Regional Sales Summary", "style": 2},
        {"type": "string", "value": "", "style": 2},
        {"type": "string", "value": "", "style": 2}
    ],
    [
        {"type": "string", "value": "Category", "style": 3},
        {"type": "string", "value": "Units Sold", "style": 3},
        {"type": "string", "value": "Total Revenue", "style": 3},
        {"type": "string", "value": "Gross Margin %", "style": 3},
        {"type": "string", "value": "Region", "style": 3},
        {"type": "string", "value": "Total Revenue", "style": 3},
        {"type": "string", "value": "Profit", "style": 3}
    ],
    # Row 1
    [
        {"type": "string", "value": "Technology", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!S:S, Cleaned_Sales_Data!O:O, "Technology")', "value": 845, "style": 6},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!O:O, "Technology")', "value": 584200.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!V:V, Cleaned_Sales_Data!O:O, "Technology")/C9', "value": 0.354, "style": 5},
        {"type": "string", "value": "North America", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!L:L, "North America")', "value": 620400.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!V:V, Cleaned_Sales_Data!L:L, "North America")', "value": 210200.0, "style": 4}
    ],
    # Row 2
    [
        {"type": "string", "value": "Furniture", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!S:S, Cleaned_Sales_Data!O:O, "Furniture")', "value": 620, "style": 6},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!O:O, "Furniture")', "value": 348100.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!V:V, Cleaned_Sales_Data!O:O, "Furniture")/C10', "value": 0.381, "style": 5},
        {"type": "string", "value": "Europe", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!L:L, "Europe")', "value": 325100.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!V:V, Cleaned_Sales_Data!L:L, "Europe")', "value": 110400.0, "style": 4}
    ],
    # Row 3
    [
        {"type": "string", "value": "Smart Gadgets", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!S:S, Cleaned_Sales_Data!O:O, "Smart Gadgets")', "value": 710, "style": 6},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!O:O, "Smart Gadgets")', "value": 156300.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!V:V, Cleaned_Sales_Data!O:O, "Smart Gadgets")/C11', "value": 0.322, "style": 5},
        {"type": "string", "value": "APAC", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!L:L, "APAC")', "value": 154200.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!V:V, Cleaned_Sales_Data!L:L, "APAC")', "value": 52100.0, "style": 4}
    ],
    # Row 4
    [
        {"type": "string", "value": "Office Supplies", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!S:S, Cleaned_Sales_Data!O:O, "Office Supplies")', "value": 930, "style": 6},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!O:O, "Office Supplies")', "value": 53980.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!V:V, Cleaned_Sales_Data!O:O, "Office Supplies")/C12', "value": 0.245, "style": 5},
        {"type": "string", "value": "LATAM", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!L:L, "LATAM")', "value": 42880.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!V:V, Cleaned_Sales_Data!L:L, "LATAM")', "value": 13720.0, "style": 4}
    ],
    [],
    # Section 2: Interactive Lookup Demo in Dashboard
    [
        {"type": "string", "value": "Interactive Order Lookup Tool (Demonstrates XLOOKUP & INDEX/MATCH)", "style": 2},
        {"type": "string", "value": "", "style": 2},
        {"type": "string", "value": "", "style": 2},
        {"type": "string", "value": "", "style": 2},
        {"type": "string", "value": "", "style": 2}
    ],
    [
        {"type": "string", "value": "Enter Order ID:", "style": 9},
        {"type": "string", "value": "ORD-2024-1005", "style": 10}, # User input cell B15
        {"type": "string", "value": "<- Change ID to test live lookup", "style": 0}
    ],
    [
        {"type": "string", "value": "Metric", "style": 3},
        {"type": "string", "value": "Lookup Result", "style": 3},
        {"type": "string", "value": "Formula Type Used", "style": 3},
        {"type": "string", "value": "Exact Formula Expression", "style": 3}
    ],
    [
        {"type": "string", "value": "Customer Name", "style": 10},
        {"type": "formula", "formula": 'XLOOKUP(B15, Cleaned_Sales_Data!A:A, Cleaned_Sales_Data!F:F, "Not Found")', "value": "Sophia Rodriguez", "style": 10},
        {"type": "string", "value": "XLOOKUP", "style": 10},
        {"type": "string", "value": '=XLOOKUP(B15, Cleaned_Sales_Data!A:A, Cleaned_Sales_Data!F:F, "Not Found")', "style": 10}
    ],
    [
        {"type": "string", "value": "Product Name", "style": 10},
        {"type": "formula", "formula": 'INDEX(Cleaned_Sales_Data!N:N, MATCH(B15, Cleaned_Sales_Data!A:A, 0))', "value": "iPhone 15 Pro", "style": 10},
        {"type": "string", "value": "INDEX + MATCH", "style": 10},
        {"type": "string", "value": '=INDEX(Cleaned_Sales_Data!N:N, MATCH(B15, Cleaned_Sales_Data!A:A, 0))', "style": 10}
    ],
    [
        {"type": "string", "value": "Sales Amount", "style": 10},
        {"type": "formula", "formula": 'XLOOKUP(B15, Cleaned_Sales_Data!A:A, Cleaned_Sales_Data!U:U, 0)', "value": 2198.0, "style": 4},
        {"type": "string", "value": "XLOOKUP", "style": 10},
        {"type": "string", "value": '=XLOOKUP(B15, Cleaned_Sales_Data!A:A, Cleaned_Sales_Data!U:U, 0)', "style": 10}
    ],
    [
        {"type": "string", "value": "Order Status", "style": 10},
        {"type": "formula", "formula": 'INDEX(Cleaned_Sales_Data!Y:Y, MATCH(B15, Cleaned_Sales_Data!A:A, 0))', "value": "Completed", "style": 10},
        {"type": "string", "value": "INDEX + MATCH", "style": 10},
        {"type": "string", "value": '=INDEX(Cleaned_Sales_Data!Y:Y, MATCH(B15, Cleaned_Sales_Data!A:A, 0))', "style": 10}
    ]
]
builder.add_sheet("Executive_Dashboard", dash_rows)

# Sheet 2: Pivot & Aggregations
pivot_rows = [
    [{"type": "string", "value": "BUSINESS PERFORMANCE PIVOT TABLES & AGGREGATIONS", "style": 1}],
    [{"type": "string", "value": "Summary matrices calculated from Cleaned_Sales_Data for executive reporting.", "style": 0}],
    [],
    [{"type": "string", "value": "Pivot 1: Revenue by Customer Segment & Product Category", "style": 2}, {"type": "string", "value": "", "style": 2}, {"type": "string", "value": "", "style": 2}, {"type": "string", "value": "", "style": 2}, {"type": "string", "value": "", "style": 2}],
    [
        {"type": "string", "value": "Customer Segment", "style": 3},
        {"type": "string", "value": "Technology", "style": 3},
        {"type": "string", "value": "Furniture", "style": 3},
        {"type": "string", "value": "Smart Gadgets", "style": 3},
        {"type": "string", "value": "Office Supplies", "style": 3},
        {"type": "string", "value": "Total Segment Sales", "style": 3}
    ],
    [
        {"type": "string", "value": "Corporate", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Corporate", Cleaned_Sales_Data!O:O, "Technology")', "value": 379730.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Corporate", Cleaned_Sales_Data!O:O, "Furniture")', "value": 226265.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Corporate", Cleaned_Sales_Data!O:O, "Smart Gadgets")', "value": 101595.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Corporate", Cleaned_Sales_Data!O:O, "Office Supplies")', "value": 35087.0, "style": 4},
        {"type": "formula", "formula": 'SUM(B5:E5)', "value": 742677.0, "style": 4}
    ],
    [
        {"type": "string", "value": "Consumer", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Consumer", Cleaned_Sales_Data!O:O, "Technology")', "value": 116840.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Consumer", Cleaned_Sales_Data!O:O, "Furniture")', "value": 69620.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Consumer", Cleaned_Sales_Data!O:O, "Smart Gadgets")', "value": 31260.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Consumer", Cleaned_Sales_Data!O:O, "Office Supplies")', "value": 10795.0, "style": 4},
        {"type": "formula", "formula": 'SUM(B6:E6)', "value": 228515.0, "style": 4}
    ],
    [
        {"type": "string", "value": "Home Office", "style": 10},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Home Office", Cleaned_Sales_Data!O:O, "Technology")', "value": 87630.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Home Office", Cleaned_Sales_Data!O:O, "Furniture")', "value": 52215.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Home Office", Cleaned_Sales_Data!O:O, "Smart Gadgets")', "value": 23445.0, "style": 4},
        {"type": "formula", "formula": 'SUMIFS(Cleaned_Sales_Data!U:U, Cleaned_Sales_Data!H:H, "Home Office", Cleaned_Sales_Data!O:O, "Office Supplies")', "value": 8098.0, "style": 4},
        {"type": "formula", "formula": 'SUM(B7:E7)', "value": 171388.0, "style": 4}
    ],
    [
        {"type": "string", "value": "Total Category Sales", "style": 3},
        {"type": "formula", "formula": 'SUM(B5:B7)', "value": 584200.0, "style": 4},
        {"type": "formula", "formula": 'SUM(C5:C7)', "value": 348100.0, "style": 4},
        {"type": "formula", "formula": 'SUM(D5:D7)', "value": 156300.0, "style": 4},
        {"type": "formula", "formula": 'SUM(E5:E7)', "value": 53980.0, "style": 4},
        {"type": "formula", "formula": 'SUM(F5:F7)', "value": 1142580.0, "style": 4}
    ],
    [],
    [{"type": "string", "value": "Pivot 2: Order Fulfillment & Status Breakdown", "style": 2}, {"type": "string", "value": "", "style": 2}, {"type": "string", "value": "", "style": 2}, {"type": "string", "value": "", "style": 2}],
    [
        {"type": "string", "value": "Order Status", "style": 3},
        {"type": "string", "value": "Order Count", "style": 3},
        {"type": "string", "value": "Total Sales ($)", "style": 3},
        {"type": "string", "value": "% of Total Revenue", "style": 3}
    ],
    [
        {"type": "string", "value": "Completed", "style": 10},
        {"type": "formula", "formula": 'COUNTIF(Cleaned_Sales_Data!Y:Y, "Completed")', "value": 984, "style": 6},
        {"type": "formula", "formula": 'SUMIF(Cleaned_Sales_Data!Y:Y, "Completed", Cleaned_Sales_Data!U:U)', "value": 936915.6, "style": 4},
        {"type": "formula", "formula": 'C12/$F$8', "value": 0.82, "style": 5}
    ],
    [
        {"type": "string", "value": "Shipped", "style": 10},
        {"type": "formula", "formula": 'COUNTIF(Cleaned_Sales_Data!Y:Y, "Shipped")', "value": 144, "style": 6},
        {"type": "formula", "formula": 'SUMIF(Cleaned_Sales_Data!Y:Y, "Shipped", Cleaned_Sales_Data!U:U)', "value": 137109.6, "style": 4},
        {"type": "formula", "formula": 'C13/$F$8', "value": 0.12, "style": 5}
    ],
    [
        {"type": "string", "value": "Refunded", "style": 10},
        {"type": "formula", "formula": 'COUNTIF(Cleaned_Sales_Data!Y:Y, "Refunded")', "value": 48, "style": 6},
        {"type": "formula", "formula": 'SUMIF(Cleaned_Sales_Data!Y:Y, "Refunded", Cleaned_Sales_Data!U:U)', "value": 45703.2, "style": 4},
        {"type": "formula", "formula": 'C14/$F$8', "value": 0.04, "style": 5}
    ],
    [
        {"type": "string", "value": "Cancelled", "style": 10},
        {"type": "formula", "formula": 'COUNTIF(Cleaned_Sales_Data!Y:Y, "Cancelled")', "value": 24, "style": 6},
        {"type": "formula", "formula": 'SUMIF(Cleaned_Sales_Data!Y:Y, "Cancelled", Cleaned_Sales_Data!U:U)', "value": 22851.6, "style": 4},
        {"type": "formula", "formula": 'C15/$F$8', "value": 0.02, "style": 5}
    ]
]
builder.add_sheet("Pivot_Analysis", pivot_rows)

# Sheet 3: Lookup Guide & Formulas
lookup_rows = [
    [{"type": "string", "value": "LOOKUP FUNCTIONS REFERENCE: XLOOKUP vs INDEX/MATCH vs VLOOKUP", "style": 1}],
    [{"type": "string", "value": "A comprehensive practical guide for Data Analysts on formula lookups.", "style": 0}],
    [],
    [
        {"type": "string", "value": "Function", "style": 3},
        {"type": "string", "value": "Syntax", "style": 3},
        {"type": "string", "value": "Advantages", "style": 3},
        {"type": "string", "value": "Limitations / Notes", "style": 3}
    ],
    [
        {"type": "string", "value": "XLOOKUP", "style": 10},
        {"type": "string", "value": "=XLOOKUP(lookup_value, lookup_array, return_array, [if_not_found], [match_mode], [search_mode])", "style": 10},
        {"type": "string", "value": "Replaces VLOOKUP/HLOOKUP; works left and right; default exact match; built-in error handling.", "style": 10},
        {"type": "string", "value": "Available in Excel 365, Excel 2021, and Google Sheets.", "style": 10}
    ],
    [
        {"type": "string", "value": "INDEX + MATCH", "style": 10},
        {"type": "string", "value": "=INDEX(return_range, MATCH(lookup_val, lookup_range, 0))", "style": 10},
        {"type": "string", "value": "Universally supported across all Excel versions; 2D matrix lookups; faster on huge sheets.", "style": 10},
        {"type": "string", "value": "Slightly more complex syntax combining two functions.", "style": 10}
    ],
    [
        {"type": "string", "value": "VLOOKUP", "style": 10},
        {"type": "string", "value": '=VLOOKUP(lookup_value, table_array, col_index, FALSE)', "style": 10},
        {"type": "string", "value": "Classic function known across legacy workbooks.", "style": 10},
        {"type": "string", "value": "Cannot look to the left; breaks if columns are inserted; requires exact column index count.", "style": 10}
    ],
    [],
    [{"type": "string", "value": "Product Catalog Lookup Table (Search by Product ID)", "style": 2}, {"type": "string", "value": "", "style": 2}, {"type": "string", "value": "", "style": 2}, {"type": "string", "value": "", "style": 2}],
    [
        {"type": "string", "value": "Lookup ID:", "style": 9},
        {"type": "string", "value": "PROD-TEC-001", "style": 10},
        {"type": "string", "value": "<- Edit Product ID to test formulas below", "style": 0}
    ],
    [
        {"type": "string", "value": "Target Field", "style": 3},
        {"type": "string", "value": "XLOOKUP Formula", "style": 3},
        {"type": "string", "value": "INDEX/MATCH Formula", "style": 3},
        {"type": "string", "value": "Evaluated Output", "style": 3}
    ],
    [
        {"type": "string", "value": "Product Name", "style": 10},
        {"type": "string", "value": '=XLOOKUP(B10, Cleaned_Sales_Data!M:M, Cleaned_Sales_Data!N:N)', "style": 10},
        {"type": "string", "value": '=INDEX(Cleaned_Sales_Data!N:N, MATCH(B10, Cleaned_Sales_Data!M:M, 0))', "style": 10},
        {"type": "formula", "formula": 'XLOOKUP(B10, Cleaned_Sales_Data!M:M, Cleaned_Sales_Data!N:N, "N/A")', "value": "MacBook Pro 16", "style": 10}
    ],
    [
        {"type": "string", "value": "Unit Price", "style": 10},
        {"type": "string", "value": '=XLOOKUP(B10, Cleaned_Sales_Data!M:M, Cleaned_Sales_Data!R:R)', "style": 10},
        {"type": "string", "value": '=INDEX(Cleaned_Sales_Data!R:R, MATCH(B10, Cleaned_Sales_Data!M:M, 0))', "style": 10},
        {"type": "formula", "formula": 'XLOOKUP(B10, Cleaned_Sales_Data!M:M, Cleaned_Sales_Data!R:R, 0)', "value": 2499.0, "style": 4}
    ],
    [
        {"type": "string", "value": "Category", "style": 10},
        {"type": "string", "value": '=XLOOKUP(B10, Cleaned_Sales_Data!M:M, Cleaned_Sales_Data!O:O)', "style": 10},
        {"type": "string", "value": '=INDEX(Cleaned_Sales_Data!O:O, MATCH(B10, Cleaned_Sales_Data!M:M, 0))', "style": 10},
        {"type": "formula", "formula": 'XLOOKUP(B10, Cleaned_Sales_Data!M:M, Cleaned_Sales_Data!O:O, "N/A")', "value": "Technology", "style": 10}
    ]
]
builder.add_sheet("Lookup_Reference", lookup_rows)

# Sheet 4: Cleaned Sales Data (1200 rows)
clean_headers = [
    "Order_ID", "Order_Date", "Ship_Date", "Ship_Mode", "Customer_ID",
    "Customer_Name", "Customer_Email", "Customer_Segment", "City", "State",
    "Country", "Region", "Product_ID", "Product_Name", "Category",
    "Subcategory", "Cost_Price", "Unit_Price", "Quantity", "Discount_Rate",
    "Sales_Amount", "Profit", "Profit_Margin_Pct", "Payment_Method", "Order_Status"
]

data_rows = [
    [{"type": "string", "value": h, "style": 3} for h in clean_headers]
]

for _, r in df.iterrows():
    row_cells = [
        {"type": "string", "value": str(r["Order_ID"]), "style": 10},
        {"type": "string", "value": str(r["Order_Date"]), "style": 7},
        {"type": "string", "value": str(r["Ship_Date"]), "style": 7},
        {"type": "string", "value": str(r["Ship_Mode"]), "style": 10},
        {"type": "string", "value": str(r["Customer_ID"]), "style": 10},
        {"type": "string", "value": str(r["Customer_Name"]), "style": 10},
        {"type": "string", "value": str(r["Customer_Email"]), "style": 10},
        {"type": "string", "value": str(r["Customer_Segment"]), "style": 10},
        {"type": "string", "value": str(r["City"]), "style": 10},
        {"type": "string", "value": str(r["State"]), "style": 10},
        {"type": "string", "value": str(r["Country"]), "style": 10},
        {"type": "string", "value": str(r["Region"]), "style": 10},
        {"type": "string", "value": str(r["Product_ID"]), "style": 10},
        {"type": "string", "value": str(r["Product_Name"]), "style": 10},
        {"type": "string", "value": str(r["Category"]), "style": 10},
        {"type": "string", "value": str(r["Subcategory"]), "style": 10},
        {"type": "number", "value": float(r["Cost_Price"]), "style": 4},
        {"type": "number", "value": float(r["Unit_Price"]), "style": 4},
        {"type": "number", "value": int(r["Quantity"]), "style": 6},
        {"type": "number", "value": float(r["Discount_Rate"]), "style": 5},
        {"type": "number", "value": float(r["Sales_Amount"]), "style": 4},
        {"type": "number", "value": float(r["Profit"]), "style": 4},
        {"type": "number", "value": float(r["Profit_Margin_Pct"]) / 100.0, "style": 5},
        {"type": "string", "value": str(r["Payment_Method"]), "style": 10},
        {"type": "string", "value": str(r["Order_Status"]), "style": 10}
    ]
    data_rows.append(row_cells)

builder.add_sheet("Cleaned_Sales_Data", data_rows)

# Build file
builder.build()
print("Built 01_excel_dashboard/sales_dashboard.xlsx successfully!")

