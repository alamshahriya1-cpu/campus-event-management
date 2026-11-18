// Rebuild the two original workbook tabs with revision 2.0 requirements and evidence.
// Requires @oai/artifact-tool; values are shared with the SRS and completion report.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FileBlob, SpreadsheetFile } from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const out=process.env.REVIEW_OUTPUT_DIR || path.join(root,'docs/rtm');
await fs.mkdir(out,{recursive:true});
const data=JSON.parse(await fs.readFile(path.join(root,'docs/review/requirements.json'),'utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root,'docs/archive/2026-10-29-baseline/RTM.xlsx')));
const team=wb.worksheets.getItem('Group Members');
const matrix=wb.worksheets.getItem('Requirements Traceability Matri');
const headers=['Req. ID','Requirement Description','Requirement Type','Priority','Use Case ID','Module','Database Entity','Test Case ID','Acceptance Criteria','Status','SRS Section','Diagram IDs','Scope','Source Files','Test Sources','Evidence IDs','Verification','Remaining Acceptance','Evidence Date'];
const values=[headers,...data.requirements.map(r=>headers.map(k=>r[k]))];
const oldTable=matrix.tables.items[0];
const tableName=oldTable.name,tableStyle=oldTable.style;
oldTable.delete();
matrix.getRange('A1:S33').values=values;
const newTable=matrix.tables.add('A1:S33',true,tableName);
newTable.style=tableStyle;newTable.showFilterButton=true;
matrix.getRange('A1:S33').format.font={name:'Calibri',size:11,color:'#19384B'};
matrix.getRange('A1:S33').format.wrapText=true;
matrix.getRange('A1:S33').format.verticalAlignment='top';
matrix.getRange('A1:S33').format.borders={preset:'all',style:'thin',color:'#D1E0E8'};
matrix.getRange('A1:S1').format={fill:'#19384B',font:{name:'Calibri',size:11,bold:true,color:'#FFFFFF'},rowHeight:40,verticalAlignment:'center',wrapText:true};
const widths=[12,64,20,12,24,26,30,20,82,14,14,28,14,62,48,24,76,76,18];
for(let i=0;i<widths.length;i++)matrix.getRangeByIndexes(0,i,33,1).format.columnWidth=widths[i];
for(let i=1;i<values.length;i++){
 const lines=Math.max(...values[i].map((v,j)=>Math.ceil(String(v).length/(widths[j]*1.12))));
 const range=matrix.getRange(`A${i+1}:S${i+1}`);
 range.format.rowHeight=Math.max(76,lines*14+14);
 range.format.fill=i%2===1?'#F0F5F8':'#FFFFFF';
}
matrix.getRange('A2:A33').format.font={bold:true};
matrix.getRange('J2:J33').format.font={bold:true};
matrix.getRange('J2:J33').dataValidation={rule:{type:'list',values:['Verified','Partial','Planned']}};
matrix.getRange('J2:J33').conditionalFormats.add('cellIs',{operator:'equal',formula:'"Verified"',format:{fill:'#DDEEE7',font:{color:'#18624D',bold:true}}});
matrix.getRange('J2:J33').conditionalFormats.add('cellIs',{operator:'equal',formula:'"Partial"',format:{fill:'#FFF2D6',font:{color:'#8B591C',bold:true}}});
matrix.freezePanes.freezeRows(1);matrix.freezePanes.freezeColumns(1);matrix.showGridLines=false;
team.getRange('B9').values=[['2.0']];
team.getRange('B9').setNumberFormat('0.0');
team.getRange('A10:B11').values=[['Review date','18 November 2026'],['Status meaning','Verified = complete under the stated evidence rule; Partial = acceptance evidence remains. Not professor sign-off.']];
team.getRange('A11:B11').format.rowHeight=65;team.getRange('B11').format.wrapText=true;
team.getRange('A13:D13').merge();team.getRange('A13').values=[['Completion against the requirements — calculated from the RTM']];
team.getRange('A13:D13').format={fill:'#19384B',font:{bold:true,color:'#FFFFFF',size:12},rowHeight:30};
team.getRange('A15:D15').values=[['Scope','Verified','Total','Completion']];
team.getRange('A15:D15').format={fill:'#EDF4F7',font:{bold:true},rowHeight:28};
const s="'Requirements Traceability Matri'!";
const status=s+'$J$2:$J$33',type=s+'$C$2:$C$33',scope=s+'$M$2:$M$33',ids=s+'$A$2:$A$33';
const metrics=[
 ['Original functional requirements',`COUNTIFS(${type},"Functional",${scope},"Original",${status},"Verified")`,`COUNTIFS(${type},"Functional",${scope},"Original")`],
 ['Added functional requirements',`COUNTIFS(${type},"Functional",${scope},"Added",${status},"Verified")`,`COUNTIFS(${type},"Functional",${scope},"Added")`],
 ['All current functional requirements',`COUNTIFS(${type},"Functional",${status},"Verified")`,`COUNTIF(${type},"Functional")`],
 ['Non-functional requirements',`COUNTIFS(${type},"Non-Functional",${status},"Verified")`,`COUNTIF(${type},"Non-Functional")`],
 ['Original total scope (18 FR + 7 NFR)',`COUNTIFS(${scope},"Original",${status},"Verified")`,`COUNTIF(${scope},"Original")`],
 ['Current total scope (25 FR + 7 NFR)',`COUNTIF(${status},"Verified")`,`COUNTA(${ids})`],
 ['Requirement rows with traceability',`COUNTA(${s}$K$2:$K$33)`,`COUNTA(${ids})`]
];
for(let i=0;i<metrics.length;i++){
 const row=16+i;team.getRange(`A${row}`).values=[[metrics[i][0]]];
 team.getRange(`B${row}:D${row}`).formulas=[[`=${metrics[i][1]}`,`=${metrics[i][2]}`,`=B${row}/C${row}`]];
}
team.getRange('B16:C22').setNumberFormat('0');team.getRange('D16:D22').setNumberFormat('0.0%');
team.getRange('A16:D22').format.rowHeight=31;
team.getRange('A21:D21').format.fill='#DDEEE7';team.getRange('A21:D21').format.font={bold:true};
team.getRange('A24:D26').merge();team.getRange('A24').values=[[data.counting_rule]];
team.getRange('A24:D26').format={wrapText:true,verticalAlignment:'center',fill:'#FFF7E7',font:{size:11,color:'#5B4825'}};
team.getRange('A24:D26').format.rowHeight=28;
team.getRange('A28:D28').merge();team.getRange('A28').values=[['Separate execution metric — saved Linux test run (E02)']];
team.getRange('A28:D28').format={fill:'#19384B',font:{bold:true,color:'#FFFFFF'},rowHeight:28};
team.getRange('A29:D30').values=[['Run','Passed','Executed','Pass rate'],['Linux / Python 3.12.14 / Django 5.2.19',110,110,null]];
team.getRange('D30').formulas=[['=B30/C30']];team.getRange('D30').setNumberFormat('0.0%');team.getRange('A29:D30').format.rowHeight=29;
team.getRange('A32:D33').merge();team.getRange('A32').values=[['Source: b3d900f4ac7c516c086708305f53ebfdebd0422d. Current saved test run: 110 passed in 3.087 s. Historical Windows/host runs had 62 tests; no exact current 110-test host or Windows transcript was supplied.']];
team.getRange('A32:D33').format.wrapText=true;team.getRange('A32:D33').format.rowHeight=29;
team.getRange('A35:D36').merge();team.getRange('A35').values=[['Use the RTM Status dropdown only when new evidence supports the change. See docs/review/COMPLETION_REPORT.pdf, requirements.json and docs/development/TEST_REPORT.md. Partial requirements: NFR001, NFR002, NFR003, NFR004 and NFR006.']];
team.getRange('A35:D36').format.wrapText=true;team.getRange('A35:D36').format.rowHeight=29;
team.getRange('A13:D36').format.font={name:'Calibri',size:11};
team.getRange('A13:D36').format.verticalAlignment='center';
team.getRange('C1:C36').format.columnWidth=14;team.getRange('D1:D36').format.columnWidth=17;
team.showGridLines=false;
wb.recalculate();
const expected=[[18,18,1],[7,7,1],[25,25,1],[2,7,2/7],[20,25,.8],[27,32,27/32],[32,32,1]];
const before=team.getRange('B16:D22').values;
if(JSON.stringify(before)!==JSON.stringify(expected))throw new Error('Unexpected completion values: '+JSON.stringify(before));
matrix.getRange('J2').values=[['Partial']];wb.recalculate();
if(team.getRange('B21').values[0][0]!==26)throw new Error('Summary did not respond to requirement status edit');
matrix.getRange('J2').values=[['Verified']];wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#N/A|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:30},maxChars:1500});
console.log('Formula error scan',JSON.stringify(errors));
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(out,'RTM.xlsx'));
const reopened=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(out,'RTM.xlsx')));
reopened.recalculate();
if(reopened.worksheets.getItem('Group Members').getRange('B21:D21').values[0][0]!==27)throw new Error('Export/reimport summary mismatch');
console.log('Verified values and status-edit response',JSON.stringify(before));
for(const [sheet,range,name] of [
 ['Group Members','A1:D11','team'],['Group Members','A13:D36','summary'],
 [matrix.name,'A1:D5','requirements-core'],[matrix.name,'H1:M5','mapping-core'],
 [matrix.name,'A20:D26','requirements-accounts'],[matrix.name,'H20:M26','mapping-accounts'],
 [matrix.name,'I27:M33','quality-status'],[matrix.name,'P27:S33','quality-evidence']
]){
 const png=await wb.render({sheetName:sheet,range,scale:1.25,format:'png'});
 await fs.writeFile(path.join(out,`rtm-${name}.png`),new Uint8Array(await png.arrayBuffer()));
}
await fs.writeFile(path.join(out,'rtm-validation.json'),JSON.stringify({requirements:32,verified:27,partial:5,summary:before,statusEditTest:'passed',exportReimport:'passed'},null,2));
