# Errors and partial answers

[Back to the test report](../README.md)

**Second API grading run only.** All 14 outcomes below scored less than 1, across 13 questions. A = official PageIndex; B = router + official. No answer generation or grading was rerun.

| Outcome | A | B |
|---|---:|---:|
| Completed material errors (0) | 2 | 0 |
| Runtime failures (0) | 3 | 0 |
| Partial answers (0.5) | 5 | 4 |
| Total below full credit | **10** | **4** |

A partial answer can be substantively correct while missing requested details or page citations. Runtime failures produced no final answer.

## Case index

| Case | Outcome | Stage | Main issue |
|---|---|---|---|
| [C300-004 / B](#c300-004-b) | Partial answer (0.5) | Citation output | Correct abstention, but no source/page citation. |
| [C300-005 / A](#c300-005-a) | Material error (0) | Document selection | Uses the passive RFP for an active-infrastructure question. |
| [C300-021 / A](#c300-021-a) | Runtime failure (0) | Runtime / turn budget | No final answer after the default ten chat turns. |
| [C300-032 / A](#c300-032-a) | Material error (0) | Evidence interpretation | Treats a historical valuation as the eventual contractor outcome. |
| [C300-045 / A](#c300-045-a) | Runtime failure (0) | Runtime / turn budget | No final answer after the default ten chat turns. |
| [C300-062 / A](#c300-062-a) | Partial answer (0.5) | Answer completeness | Omits additional actuarial studies as requested. |
| [C300-067 / A](#c300-067-a) | Partial answer (0.5) | Answer completeness | Omits FASB Topics 820 and 946 for fund statements. |
| [C300-074 / A](#c300-074-a) | Partial answer (0.5) | Answer completeness | Omits the $20bn aggregate / two public clients / one above $5bn tests. |
| [C300-074 / B](#c300-074-b) | Partial answer (0.5) | Answer completeness | Omits the $20bn aggregate / two public clients / one above $5bn tests. |
| [C300-083 / B](#c300-083-b) | Partial answer (0.5) | Answer completeness | Omits PCS hedge-fund and alternative-real-asset scope. |
| [C300-086 / A](#c300-086-a) | Runtime failure (0) | Runtime / turn budget | No final answer after the default ten chat turns. |
| [C300-101 / B](#c300-101-b) | Partial answer (0.5) | Citation output | Correct comparison; section/exhibit citations have no page locators. |
| [C300-114 / A](#c300-114-a) | Partial answer (0.5) | Answer completeness | Omits Delaware's general $1bn / ten-year rule. |
| [C300-115 / A](#c300-115-a) | Partial answer (0.5) | Answer completeness | Omits individualized counseling and participant-specific advice. |

The four B cases selected the relevant documents and read the annotated evidence pages. Their gaps arose in answer completeness or citation output. For A/114 and A/115, missing details were also present in the returned text on alternative pages, even though the exact annotated page was not read.

## Questions, answers and deductions

Each case shows the original question and API deduction. Expand the answer to inspect it. Displayed PDF links point to the public sources in the inventory; original answer strings and hashes remain in [answers.jsonl](../data/answers.jsonl).

<a id="c300-004-b"></a>

### C300-004 / B

**Question:** Using only the supplied Invest Europe ESG questionnaire, report the assessed company’s actual annual greenhouse-gas emissions in tonnes.

**Result:** Partial answer (0.5). **Stage:** Citation output.

**API deduction:** Correctly explains that the unanswered questionnaire provides no actual annual emissions figure, but gives no source/page citation.

<details>
<summary>Actual answer</summary>

The questionnaire does not report an assessed company’s actual annual greenhouse-gas emissions in tonnes. It is a blank due-diligence template that asks companies to provide emissions information, but contains no company response or emissions figure.

</details>

**Reference pages:** [Invest Europe ESG Due Diligence Questionnaire for Private Equity Investors and Portfolio Companies, PDF p. 6](<https://www.investeurope.eu/media/1777/invest-europe_esg_dd_questionnaire.pdf>).

<a id="c300-005-a"></a>

### C300-005 / A

**Question:** Does LACERS’ active listed infrastructure RFP confine all products exclusively to the named S&P benchmark?

**Result:** Material error (0). **Stage:** Document selection.

**API deduction:** Cites the passive RFP instead of the active RFP, incorrectly says the products must be passive, and does not establish the active RFP’s express permission to select products using other benchmarks.

**Required facts omitted or not established:**

- The active RFP permits selection of products managed against other listed-infrastructure benchmarks.

<details>
<summary>Actual answer</summary>

No. LACERS names the **S&P Global Listed Infrastructure Index as its proposed strategy benchmark**, but the RFP does not say every proposed product must use it as its own internal benchmark. It asks each proposer to identify the benchmark it typically uses and explain why it is appropriate. Products still must focus on **passive listed infrastructure** and meet the RFP’s other requirements. [LACERS RFP, pp. 3, 17](<https://www.nepc.com/wp-content/uploads/2026/04/passively_managed_global_listed_infrastructure_rfp_document.pdf>)

</details>

**Reference pages:** [Microsoft Word - 20260310 Bd Rpt - Actively and Passively Managed Global Listed Infrastructure RFP, PDF p. 3](<https://www.lacers.org/sites/main/files/file-attachments/actively_managed_global_listed_infrastructure_rfp_document.pdf?1775710525=>).

<a id="c300-021-a"></a>

### C300-021 / A

**Question:** What proposal length and font rules apply to Laguna Niguel’s Section115 trust procurement, and what is excluded from its page limit?

**Result:** Runtime failure (0). **Stage:** Runtime / turn budget.

**API deduction:** Generation failed; no answer was provided.

**Required facts omitted or not established:**

- 20-page maximum and 12-point font
- Transmittal letter and résumés count toward the limit
- Index/table of contents, tables, charts, graphic exhibits, and pricing forms are excluded

**Actual outcome:** No final answer. Recorded error: `The agent did not finish within max_turns (the default limit). Raise max_turns, or narrow the question.`

**Reference pages:** [RFP_Section_115_Trust FINAL, PDF p. 3](<https://www.cityoflagunaniguel.org/DocumentCenter/View/17709>).

<a id="c300-032-a"></a>

### C300-032 / A

**Question:** Using only Illinois’ 2026 custody RFP, give the actual year-end market value of the corporate and municipal bonds ultimately held by the successful contractor.

**Result:** Material error (0). **Stage:** Evidence interpretation.

**API deduction:** Mistakes a historical June 30 pricing input for the requested observed outcome. The RFP does not establish the successful contractor’s ultimate holdings or their year-end value.

**Required facts omitted or not established:**

- The actual year-end value of bonds ultimately held by the successful contractor cannot be determined from this prospective RFP.

<details>
<summary>Actual answer</summary>

The corporate and municipal bonds had a **combined market value of $299,844,417 as of June 30, 2026**, according to the trust-statement figure in Appendix B of Illinois’ 2026 custody RFP. This is the year-end value, not the managers’ $300 million investment authority. [Illinois custody RFP, pp. 3, 33](<https://www.illinoistreasurer.gov/wp-content/uploads/2026/09/RFP-Custody-and-Safekeeping-Services-370-500-27-045.pdf>)

</details>

**Source nuance:** $299,844,417 is a real historical figure in Appendix B. The error is assigning it to the eventual successful contractor, whose actual outcome this prospective RFP cannot establish.

**Reference pages:** [RFP Custody and Safekeeping Services 370-500-27-045, PDF p. 3](<https://www.illinoistreasurer.gov/wp-content/uploads/2026/09/RFP-Custody-and-Safekeeping-Services-370-500-27-045.pdf>).

<a id="c300-045-a"></a>

### C300-045 / A

**Question:** What was NYSDC Stable Income Fund’s reported duration at 30 September 2025?

**Result:** Runtime failure (0). **Stage:** Runtime / turn budget.

**API deduction:** Generation failed; no answer was provided.

**Required facts omitted or not established:**

- Reported duration of 3.3 years

**Actual outcome:** No final answer. Recorded error: `The agent did not finish within max_turns (the default limit). Raise max_turns, or narrow the question.`

**Reference pages:** [NYSDC RFP – SVSM 2026, PDF p. 4](<https://www.callan.com/uploads/2026/01/19ed33f462726eefaf4ce15cbd31446c/nysdc-rfp-svsm-2026.pdf>).

<a id="c300-062-a"></a>

### C300-062 / A

**Question:** Combine OPERS’ 2022 actuarial-audit background with NMERB’s 2022 actuarial pricing scope. Distinguish valuation/experience-study frequency from the contract’s price and maximum duration.

**Result:** Partial answer (0.5). **Stage:** Answer completeness.

**API deduction:** Correctly explains the frequencies, pricing structure and four-year maximum with page citations, but does not state that NMERB’s contract provides for additional studies as requested.

**Required facts omitted or not established:**

- NMERB’s contract provides for additional studies as requested.

<details>
<summary>Actual answer</summary>

OPERS’ 2022 RFP provides the **audit background**: its board must obtain actuarial valuations annually and experience studies at least every three years. The RFP sought an *independent review* of its incumbent actuary’s work for OPERS and URSJJ, including replication of the June 30, 2021 valuations and review of the most recent experience study. Those frequencies describe OPERS’ underlying actuarial work, not the price or term of NMERB’s contract. [OPERS RFP, pp. 5, 9–10](<https://www.opers.ok.gov/wp-content/uploads/2022/02/2022-02-RFP-Actuarial-Audit-Services-515-22-100.pdf>)

NMERB’s 2022 RFP instead sought a firm to **perform actuarial services**: valuations for fiscal years ending June 30, 2022–2025, one experience investigation as of June 30, 2023, GASB 67/68 reporting, annual COLA letters, and general consulting. Its contract had a **maximum term of four years**. For pricing, bidders were to quote a **fixed annual fee** covering each year’s valuation, GASB reporting, and COLA letter; a **separate fixed fee** for the experience investigation; and a **flat hourly fee** for general consulting and special projects. The RFP specifies a pricing structure, not an awarded dollar price. [NMERB RFP, pp. 5, 26–28, 42](<https://www.erb.nm.gov/wp-content/uploads/2021/12/Actuarial_RFP_final.pdf>)

</details>

**Reference pages:** [OKLAHOMA PUBLIC EMPLOYEES RETIREMENT SYSTEM, PDF p. 5](<https://www.opers.ok.gov/wp-content/uploads/2022/02/2022-02-RFP-Actuarial-Audit-Services-515-22-100.pdf>); [Actuarial_RFP_final, PDF p. 5](<https://www.erb.nm.gov/wp-content/uploads/2021/12/Actuarial_RFP_final.pdf>).

<a id="c300-067-a"></a>

### C300-067 / A

**Question:** Build a calendar of recurring deliverables from Illinois’ infrastructure-development advisor, 2022 Secure Choice investment-consultant and 2026 stewardship-consultant RFPs. Cover fund statements, fee review and proxy-vote rationales.

**Result:** Partial answer (0.5). **Stage:** Answer completeness.

**API deduction:** A well-supported calendar covers fee reviews and quarterly and annual proxy-vote rationales, but omits the required accounting standards for recipient-fund statements.

**Required facts omitted or not established:**

- Recipient funds’ quarterly and annual financial statements must comply with FASB Topics 820 and 946.

<details>
<summary>Actual answer</summary>

## Recurring deliverables calendar

| Cadence | Advisor or consultant | Deliverable |
|---|---|---|
| **Monthly** | Infrastructure Development Account (IDA) advisor | Separately account for and report IDA investment commitments and subsequent earnings. [IDA RFP, p. 8] |
| **Quarterly** | IDA advisor | Ensure recipient-fund financial reports arrive **within 45–90 calendar days after quarter-end**. Make quarterly financial statements and itemized partners’ capital statements electronically accessible; the latter must cover calls, distributions, and realized and unrealized gains and losses. Deliver standardized fund-characteristics and consolidated investment reports covering cash flows, values, returns, benchmarks, fees, and updates; report recommendations, commitments, Illinois economic impact, investment details, and portfolio diversification. Present an update to the Treasurer and its advisers. [IDA RFP, pp. 6–8] |
| **Quarterly** | Secure Choice investment consultant | Report investment returns, allocation, historical performance, attribution, fees, underlying funds, and holdings—more often if requested. Attend quarterly fund due-diligence and review meetings, and meet Treasurer staff to discuss reports and analysis **at least four times a year**. [Secure Choice RFP, pp. 5–6] |
| **Quarterly** | Stewardship consultant | Prepare **detailed, individualized proxy-vote rationales** and attend a proxy oversight meeting. Highlight notable votes, especially those not covered by the current policy, for possible policy additions. Meet Treasurer representatives at least once each calendar quarter. [Stewardship RFP, pp. 4–5] |
| **Annually** | IDA advisor | Ensure recipient funds provide **audited financial statements within 90 calendar days after fiscal year-end**. Prepare a public report summarizing fund performance, Illinois economic impact, investment options and returns, and other program-impact information. Facilitate Treasurer attendance at recipient funds’ annual board meetings. [IDA RFP, pp. 6, 8] |
| **Annually** | Secure Choice investment consultant | Review the Investment Policy Statement, guidelines, and processes; review asset allocation, underlying-fund fees, and benchmarks. Produce a cost and industry comparison of administration, investment-management, and other program fees, plus detailed program- and fund-level performance-attribution benchmarking. [Secure Choice RFP, pp. 4–5] |
| **Annually** | Stewardship consultant | Review the Sustainable Investment and Proxy Voting Policy Statements; prepare annual detailed, individualized proxy-vote rationales. Help produce and distribute the Annual Sustainability Investment Report, including votes, corporate engagements, and collaborative partnerships. [Stewardship RFP, pp. 4–5] |

**Event-driven rather than calendar-dated:** The IDA advisor must ensure recipient funds give electronic notice of capital calls and distributions **at least five days in advance**. Secure Choice reports may be requested more frequently than quarterly; stewardship voting, engagement, and monitoring continue as relevant events arise. The RFPs do not assign fixed calendar dates to the annual reviews or reports beyond the IDA fund-statement deadlines above. [IDA RFP, p. 6; Secure Choice RFP, p. 5; Stewardship RFP, pp. 4–5]

</details>

**Reference pages:** [RFP Illinois Infrastructure Development Account Investment Advisor 370-500-23-034, PDF p. 6](<https://illinoistreasurer.gov/TWOCMS/media/doc/rfp%20illinois%20infrastructure%20development%20account%20investment%20advisor%20370-500-23-034.pdf>); [Request for Proposals for Investment & Administrative Consulting Services, PDF p. 5](<https://illinoistreasurergovprod.blob.core.usgovcloudapi.net/twocms/media/doc/request%20for%20proposals%20investment%20consulting%20services%20370-200-22-014.pdf>); [RFP Stewardship and Sustainable Investment Consulting Services 370-500-26-040, PDF p. 4](<https://stomainsitewp.azurewebsites.us/wp-content/uploads/2026/04/RFP-Stewardship-and-Sustainable-Investment-Consulting-Services-370-500-26-040.pdf>).

<a id="c300-074-a"></a>

### C300-074 / A

**Question:** Compare reference/client evidence in ACTA’s actuarial-services RFP and SamCERA’s 2025 general-consultant RFP. Why are three contactable references not automatically sufficient for SamCERA?

**Result:** Partial answer (0.5). **Stage:** Answer completeness.

**API deduction:** Accurately compares the reference requirements and explains why contactable references alone are insufficient, but omits SamCERA’s specific minimum client-asset and public-pension thresholds.

**Required facts omitted or not established:**

- SamCERA requires institutional fund clients with at least $20 billion in aggregate assets, including two public-pension clients, one with more than $5 billion in assets.

<details>
<summary>Actual answer</summary>

**ACTA** asks for at least three client references with contact names and information as part of the firm’s relevant-experience narrative. For projects used to demonstrate qualifications, it also asks when the work was done and which proposed team members participated. Its evaluation form asks whether references confirm similar work. [ACTA RFP, pp. 6, 13](<https://www.acta.org/wp-content/uploads/2026/02/Acturarial-Services-RFP-final.pdf>)

**SamCERA** asks for a more specific body of client evidence. Its three references must be **current, full-service general-consulting retainer clients** for whom the firm has performed work similar to this RFP. For each, the proposer must give contact details, plan asset value, and the number of managers by asset class. Separately, it must identify its five largest public-pension clients and disclose former client relationships from the past three years, including termination reasons and contacts. SamCERA may contact current and former clients and evaluates positive references and background checks, including service quality, collaboration with staff, and timely responses. [SamCERA RFP, pp. 14, 18, 24–25](<https://content.samcera.gov/wp-content/uploads/2025/05/samcera_investment_consultant_rfp_2025.pdf>)

Thus, **three people willing to take a call satisfy only the contact-count aspect**, not SamCERA’s requirements about the clients’ current status, engagement type, comparable work, and supporting plan details. Nor do references substitute for its separately screened minimum qualifications, such as the required public-pension client base, scale, and lead-consultant experience; incomplete evidence may be treated as deficient. [SamCERA RFP, pp. 4–5, 17, 25](<https://content.samcera.gov/wp-content/uploads/2025/05/samcera_investment_consultant_rfp_2025.pdf>)

</details>

**Reference pages:** [REQUEST FOR PROPOSALS, PDF p. 6](<https://www.acta.org/wp-content/uploads/2026/02/Acturarial-Services-RFP-final.pdf>); [Company Name Your business tag line here. Request for Proposal GENERAL INVESTMENT CONSULTANT SERVICES Proposal due date June 30, 2025 by 5:00 p.m. Pacific Time Proposals must be su, PDF p. 4](<https://content.samcera.gov/wp-content/uploads/2025/05/samcera_investment_consultant_rfp_2025.pdf>).

<a id="c300-074-b"></a>

### C300-074 / B

**Question:** Compare reference/client evidence in ACTA’s actuarial-services RFP and SamCERA’s 2025 general-consultant RFP. Why are three contactable references not automatically sufficient for SamCERA?

**Result:** Partial answer (0.5). **Stage:** Answer completeness.

**API deduction:** Provides a supported comparison of the reference requirements, but does not state the numerical client qualifications central to why three references alone are insufficient.

**Required facts omitted or not established:**

- SamCERA requires institutional fund clients with at least $20 billion in aggregate assets, including two public-pension clients, one with more than $5 billion in assets.

<details>
<summary>Actual answer</summary>

**ACTA** asks for at least three client references, with contact names and information, alongside a narrative of relevant actuarial work. For projects cited as evidence, the proposer must give the years performed and identify any proposed team members involved. ACTA’s evaluation form asks whether references confirm similar work. [ACTA RFP, pp. 6, 13](<https://www.acta.org/wp-content/uploads/2026/02/Acturarial-Services-RFP-final.pdf>)

**SamCERA** asks for a more specific set of three: they must be *current, full-service general-investing-consulting retainer clients* for whom the firm has done work similar to the RFP. Each reference needs a named contact with title, address, phone and email, **plus the plan’s asset value and number of managers by asset class**. SamCERA separately asks for its five largest public-pension clients and details and contacts for former clients from the last three years; it may contact current or former clients itself. [SamCERA RFP, pp. 24–25, 14](<https://content.samcera.gov/wp-content/uploads/2025/05/samcera_investment_consultant_rfp_2025.pdf>)

Thus, **three people willing to take a call satisfy only part of SamCERA’s reference request**. The clients and work must fit the specified relationship, and the proposal must document their scale and portfolio complexity. References also do not substitute for SamCERA’s separate minimum qualifications—including qualifying public-pension clients, a recently experienced lead consultant, and public-pension fiduciary experience—or guarantee a favorable background check on service quality, responsiveness, and collaboration with staff. [SamCERA RFP, pp. 4–5, 17–18](<https://content.samcera.gov/wp-content/uploads/2025/05/samcera_investment_consultant_rfp_2025.pdf>)

</details>

**Reference pages:** [REQUEST FOR PROPOSALS, PDF p. 6](<https://www.acta.org/wp-content/uploads/2026/02/Acturarial-Services-RFP-final.pdf>); [Company Name Your business tag line here. Request for Proposal GENERAL INVESTMENT CONSULTANT SERVICES Proposal due date June 30, 2025 by 5:00 p.m. Pacific Time Proposals must be su, PDF p. 4](<https://content.samcera.gov/wp-content/uploads/2025/05/samcera_investment_consultant_rfp_2025.pdf>).

<a id="c300-083-b"></a>

### C300-083 / B

**Question:** Which MassPRIM advisory procurement should a team use for OCO/PCS strategy advice, and how does that scope differ from the public-markets advisory definition? Explain the treatment of value-added fixed income.

**Result:** Partial answer (0.5). **Stage:** Answer completeness.

**API deduction:** Correctly identifies the OCO/PCS procurement, contrasts the public-markets scope, and explains the value-added fixed-income connection with page citations. It omits what PCS covers.

**Required facts omitted or not established:**

- PCS covers stable-value and directional hedge funds and alternative real assets.

<details>
<summary>Actual answer</summary>

Use MassPRIM’s **October 2025 Alternative Investment Strategies Advisory Services RFP** for OCO/PCS strategy advice. It expressly covers Other Credit Opportunities (OCO) and Portfolio Completion Strategies (PCS), with proposals permitted for ongoing general advice, project-based work, or both. General-service respondents can specify OCO, PCS, or both. The work includes allocation and portfolio construction, benchmarking, manager oversight and selection, due diligence, and risk analysis. [Alternative Investment Strategies RFP, pp. 7–8](<https://www.mapension.com/wp-content/uploads/2025/10/Alternative-Investment-Strategies-Advisory-Services-RFP_Final.pdf>)

The **October 2022 Public Markets Advisory Services RFP** defines its scope more broadly by asset class: global equities, core fixed income, and value-added fixed income. It calls for public-markets portfolio planning, quarterly performance and holdings analysis, and manager searches across equity and fixed-income markets. [Public Markets Advisory Services RFP, p. 7](<https://www.mapension.com/wp-content/uploads/2022/10/Public-Markets-Advisory-Services-RFP.pdf>)

**Value-added fixed income is the overlap, not a reason to switch procurements.** The public-markets definition includes the overall value-added fixed-income asset class, but the alternative-strategies RFP specifically places **OCO within that portfolio** and seeks advice on OCO’s primarily less-liquid, non-public corporate, structured, and asset-based credit opportunities. For OCO/PCS strategy advice, use the OCO/PCS-specific RFP rather than assuming all value-added fixed-income advice belongs under the public-markets RFP. [Alternative Investment Strategies RFP, p. 7](<https://www.mapension.com/wp-content/uploads/2025/10/Alternative-Investment-Strategies-Advisory-Services-RFP_Final.pdf>); [Public Markets Advisory Services RFP, p. 7](<https://www.mapension.com/wp-content/uploads/2022/10/Public-Markets-Advisory-Services-RFP.pdf>)

</details>

**Reference pages:** [Pension reserves, PDF p. 7](<https://www.mapension.com/wp-content/uploads/2025/10/Alternative-Investment-Strategies-Advisory-Services-RFP_Final.pdf>); [Pension reserves, PDF p. 7](<https://www.mapension.com/wp-content/uploads/2022/10/Public-Markets-Advisory-Services-RFP.pdf>).

<a id="c300-086-a"></a>

### C300-086 / A

**Question:** Would $10 million of errors-and-omissions insurance meet the stated coverage floors in Baltimore’s recordkeeper and 2022 financial-audit RFPs?

**Result:** Runtime failure (0). **Stage:** Runtime / turn budget.

**API deduction:** Generation failed; no answer was provided.

**Required facts omitted or not established:**

- Recordkeeper $5 million floor
- Financial-audit $25 million floor
- $10 million meets the first floor but falls $15 million short of the second

**Actual outcome:** No final answer. Recorded error: `The agent did not finish within max_turns (the default limit). Raise max_turns, or narrow the question.`

**Reference pages:** [Recordkeeper RFP, PDF p. 9](<https://www.bcers.org/wp-content/uploads/2025/01/Recordkeeper-RFP-.pdf>); [RFP Financial Auditing Services 2022, PDF p. 16](<https://www.bcers.org/wp-content/uploads/2022/01/RFP-Financial-Auditing-Services-2022.pdf>).

<a id="c300-101-b"></a>

### C300-101 / B

**Question:** What changed in FPIF’s emerging-market-debt strategy submission choices from its 2023 RFP to January 2026? Could a standalone hard-currency-only submission simply be carried forward?

**Result:** Partial answer (0.5). **Stage:** Citation output.

**API deduction:** Correctly explains both RFPs and why a hard-currency-only proposal cannot simply carry over, but its citations identify sections and exhibits without page locators.

<details>
<summary>Actual answer</summary>

The submission choice narrowed. **In 2023**, FPIF accepted up to **one blended strategy and one hard-currency strategy**, and managers did not have to offer both. A standalone hard-currency submission was therefore an option. The RFP also required separate product-specific answers and Excel workbooks if a manager proposed both. [2023 RFP, §1.2 and §3.2](<https://ifpif.org/wp-content/uploads/2023/11/FPIF-EMD-Fixed-Income-RFP.pdf>), [Exhibit E](<https://ifpif.org/wp-content/uploads/2023/11/FPIF-EMD-Fixed-Income-RFP.pdf>)

**In January 2026**, FPIF requested **one blended strategy** capable of allocating across hard-currency, local-currency, and hard-currency corporate debt. It no longer listed a separate hard-currency strategy as a submission option. [2026 RFP, §1.2](<https://ifpif.org/wp-content/uploads/2026/01/FPIF-EMD-Fixed-Income-RFP-1.23.2026.pdf>)

**No:** a standalone hard-currency-only proposal could not simply be carried forward as the specified 2026 submission. A manager would need to propose a qualifying blended strategy and prepare its response for the 2026 RFP.

</details>

**Reference pages:** [FPIF-EMD-Fixed-Income-RFP, PDF p. 3](<https://ifpif.org/wp-content/uploads/2023/11/FPIF-EMD-Fixed-Income-RFP.pdf>); [FPIF-EMD-Fixed-Income-RFP 1.23.2026, PDF p. 3](<https://ifpif.org/wp-content/uploads/2026/01/FPIF-EMD-Fixed-Income-RFP-1.23.2026.pdf>).

<a id="c300-114-a"></a>

### C300-114 / A

**Question:** A firm headquartered in Delaware has $300 million AUM and five years of continuous performance managing that amount. Compare the Delaware endowment RFP’s local-firm alternative with Colorado’s 2022 dignified-retirement investment-manager floor.

**Result:** Partial answer (0.5). **Stage:** Answer completeness.

**API deduction:** Correctly applies the Delaware alternative and Colorado floor with page citations, but omits the general Delaware rule that makes the local provision an alternative.

**Required facts omitted or not established:**

- Delaware’s general rule requires $1 billion AUM and ten years of continuous performance.

<details>
<summary>Actual answer</summary>

The firm **meets Delaware’s local-firm alternative**: the endowment RFP permits a firm with its *primary headquarters in Delaware* to apply with at least **$250 million AUM** and **five years of continuous performance managing at least that amount**. Its $300 million AUM and stated track record clear those thresholds. This makes it eligible to submit a proposal, not guaranteed an award. [Delaware RFP, p. 5](<https://bidcondocs.delaware.gov/TRE/TRE_20103Endowmgrs_rfp.pdf>)

It **does not meet Colorado’s 2022 firm-level floor** for the Partnership for a Dignified Retirement: Colorado requires at least **$500 million in total AUM**, alongside five years of asset-management experience. The firm is **$200 million short** on AUM; Delaware headquarters does not create an exception in Colorado’s stated requirements. Colorado also imposes separate requirements on each proposed strategy and investment vehicle. [Colorado RFP, pp. 6–7](<https://cri.georgetown.edu/wp-content/uploads/2022/06/CSSP-Investment-Management-Services-RFP-TRES-NP-22-002-June-8-2022.pdf>)

</details>

**Reference pages:** [REQUEST FOR PROPOSALS FOR INVESTMENT MANAGEMENT SERVICES ISSUED, PDF p. 1](<https://bidcondocs.delaware.gov/TRE/TRE_20103Endowmgrs_rfp.pdf>); [Microsoft Word - CSSP-Investment-Management-Services-RFP-TRES-NP-22-002-June-8-2022.docx, PDF p. 6](<https://cri.georgetown.edu/wp-content/uploads/2022/06/CSSP-Investment-Management-Services-RFP-TRES-NP-22-002-June-8-2022.pdf>).

<a id="c300-115-a"></a>

### C300-115 / A

**Question:** Within the PSPRS documents, distinguish the service aimed at members making DC-plan decisions from the service educating trustees and monitoring the DC plans. Identify the intended audience and recordkeeper-related role of each.

**Result:** Partial answer (0.5). **Stage:** Answer completeness.

**API deduction:** Correctly identifies the audiences and recordkeeper-related roles, with supporting page citations, but describes the member service as education without stating that it provides individualized counseling and participant-specific plan advice.

**Required facts omitted or not established:**

- Individualized counseling and participant-specific plan advice are part of the external education provider’s service.

<details>
<summary>Actual answer</summary>

The two PSPRS solicitations serve different audiences:

- **External education provider:** Primarily serves **members** making retirement-plan decisions, especially new members choosing among DB, DC, and hybrid options and deciding DC contributions and investments. Its recordkeeper-related role is to **work alongside DC recordkeepers and other plan providers** in delivering member education; the RFP requires experience working with recordkeepers, not selecting or overseeing one. [External Education Provider RFP, pp. 2–5](<https://www.psprs.com/wp-content/uploads/2026/01/DC-Education-RFP-A1.pdf>)
- **DC plans investment advisor/consultant:** Primarily serves the **DC Committee and PSPRS Board of Trustees**, educating them and monitoring the four DC plans’ investments, policies, performance, and fees. Its recordkeeper-related role is to **help select and oversee service providers**, including assisting with the next recordkeeper RFP when the current contract comes due. [DC Plans Investment Advisor/Consultant RFP, pp. 1–3](<https://www.psprs.com/wp-content/uploads/2025/01/PSPRS-RFP-DC-Plans-Investment-Advisor-Consultant.pdf>)

</details>

**Reference pages:** [DC Education RFP A1, PDF p. 1](<https://www.psprs.com/wp-content/uploads/2026/01/DC-Education-RFP-A1.pdf>); [PSPRS RFP – DC Plans Investment Advisor & Consultant, PDF p. 1](<https://www.psprs.com/wp-content/uploads/2025/01/PSPRS-RFP-DC-Plans-Investment-Advisor-Consultant.pdf>).
