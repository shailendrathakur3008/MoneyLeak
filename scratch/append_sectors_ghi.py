# -*- coding: utf-8 -*-
"""
Appends Sectors G (Telecom & Digital), H (Metals & Mining), and I (Infra & Real Estate)
"""
import sys
import os
import pprint

root_dir = r"c:\Users\shail\OneDrive\Documents\MoneyLeak"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scratch.generate_catalogue_modules import make_stock
from app.services.catalogue.stocks import STOCKS_CATALOGUE

stocks = list(STOCKS_CATALOGUE)

# =============================================================================
# G. Telecommunications and Digital Services (6 stocks)
# =============================================================================
stocks.extend([
    make_stock(
        'bharti-airtel', 'Bharti Airtel Limited', 'BHARTIARTL',
        'Large-Cap Telecom & Digital Infrastructure', 'Medium', 5, 1680.0, '> 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR',
        'Telecom duopoly leader with over 350 million Indian mobile users, commanding industry-highest ARPU, rapid enterprise 5G cloud adoption, and high Airtel Africa cash flows.',
        'Sustained mobile tariff hike cycle, 5G enterprise solutions, Airtel Payments Bank, and data center scaling (Nxtra).',
        ['Dominant pricing power in a structured telecom duopoly driving industry-leading ARPU expansion', 'High free cash flow generation enabling sustained balance sheet deleveraging', 'Strong non-mobile growth engines: Airtel Business (B2B), DTH, and Airtel Payments Bank'],
        ['Capital-intensive operations requiring continuous spectrum acquisition and 5G network capex', 'Regulatory exposure to statutory government AGR dues and spectrum fees', 'Direct equity market risks apply during telecom sector corrections']
    ),
    make_stock(
        'vodafone-idea', 'Vodafone Idea Limited', 'IDEA',
        'Telecom Service Provider (Turnaround)', 'High', 9, 9.20, '3 - 5 Years',
        '12.0% - 20.0% CAGR', '5Y Historical CAGR',
        'Third-largest private telecom operator undergoing capital turnaround following landmark Rs 24,000 Crore equity fundraise, expanding 4G coverage and selective 5G rollouts.',
        'High-risk turnaround play on 4G network expansion, bank debt refinancing, and potential government AGR relief.',
        ['Substantial customer base of over 210 million subscribers and valuable nationwide spectrum holdings', 'Government of India is the largest single shareholder holding over 23% equity stake', 'High operational leverage: modest tariff hikes and subscriber churn reduction create sharp EBITDA expansion'],
        ['Massive outstanding liabilities toward government AGR and spectrum deferrals due from FY26 onwards', 'Persistent monthly subscriber loss to telecom duopoly leaders Reliance Jio and Bharti Airtel', 'Extremely high equity volatility and speculative turnaround risk']
    ),
    make_stock(
        'indus-towers', 'Indus Towers Limited', 'INDUSTOWER',
        'Large-Cap Telecom Passive Infrastructure', 'High', 7, 360.0, '3 - 5 Years',
        '13.5% - 17.0% CAGR', '5Y Historical CAGR',
        'World’s largest telecom tower company outside China, operating over 220,000 towers across all 22 telecom circles in India with high sharing tenancy ratios.',
        'Rapid 5G small-cell densification, rural co-location tenancies, and past trade receivables collection turnaround.',
        ['Near-irreplaceable physical footprint across prime urban and highway telecom tower locations', 'Anchor long-term tenancy agreements with Bharti Airtel providing highly predictable cash flows', 'Substantial operational leverage as telcos add 5G equipment onto existing tower infrastructure'],
        ['Customer concentration risk with heavy historical exposure to Vodafone Idea payment collections', 'High diesel generator fuel costs at rural off-grid tower sites', 'Equity beta during telecom industry regulatory and litigation shifts']
    ),
    make_stock(
        'tata-communications', 'Tata Communications Limited', 'TATACOMM',
        'Large-Cap Global Digital Ecosystem & Cloud', 'Medium', 5, 1980.0, '> 5 Years',
        '14.0% - 17.0% CAGR', '5Y Historical CAGR',
        'Digital ecosystem enabler of the Tata Group, operating the world’s largest wholly-owned subsea fiber network carrying over 30% of global internet routes.',
        'Global enterprise digital fabric transition, cybersecurity, cloud edge networking (NetFoundry), and IoT Smart Mobility.',
        ['Strategic global infrastructure moat: Tier-1 subsea fiber cable network connecting over 190 countries', 'Successful transition from legacy wholesale voice to high-margin digital enterprise platforms', 'Strong Tata Group corporate governance and high credit rating'],
        ['High capital expenditure required in submarine cable maintenance and continuous tech upgrades', 'Pricing erosion in legacy basic international data connectivity lines', 'Foreign exchange currency fluctuations across international revenue streams']
    ),
    make_stock(
        'info-edge-india', 'Info Edge (India) Limited (Naukri)', 'NAUKRI',
        'Large-Cap Internet Platforms & Consumer Tech', 'High', 7, 7850.0, '3 - 5 Years',
        '15.5% - 19.5% CAGR', '5Y Historical CAGR',
        'India’s premier internet platform pioneer operating monopoly recruitment portal Naukri.com, 99acres real estate, Jeevansathi, alongside early venture stakes in Zomato and Policybazaar.',
        'Indian white-collar recruitment revival, IT hiring upcycle, and substantial value unlocking in consumer internet unicorn stakes.',
        ['Uncontested monopoly in white-collar recruitment with Naukri generating high cash flows and 55%+ operating margins', 'Pioneering venture capital track record creating immense value in Zomato and Policybazaar', 'Fortress debt-free cash balance sheet providing high strategic capital flexibility'],
        ['High sensitivity of core Naukri recruitment billing to cyclical IT services hiring freezes', 'Gestational operating losses in competitive online real estate portal business (99acres)', 'High valuation multiples make the stock volatile during consumer tech selloffs']
    ),
    make_stock(
        'pb-fintech', 'PB Fintech Limited (Policybazaar)', 'POLICYBZR',
        'Large-Cap Online Insurance & Credit Platform', 'High', 8, 1720.0, '3 - 5 Years',
        '16.0% - 21.0% CAGR', '5Y Historical CAGR',
        'India’s dominant digital insurance marketplace (Policybazaar commanding > 90% online market share) and digital credit platform (Paisabazaar), delivering operating profitability.',
        'Underpenetrated retail health and term insurance adoption, physical POSP store expansion, and high operating leverage.',
        ['Unchallenged digital distribution monopoly in online term life and retail health insurance comparisons', 'Asset-light marketplace model generating strong operating leverage as renewal premiums compound with zero acquisition cost', 'Strong net cash position and rapid expansion into corporate health insurance and offline retail advisory'],
        ['Regulatory changes by IRDAI on distributor commission disclosure and Bima Sugam platform launch', 'High sensitivity to unsecured consumer credit cycles in Paisabazaar lending channel', 'Elevated valuation multiples elevate stock price beta during market drawdowns']
    )
])

# =============================================================================
# H. Metals, Mining and Materials (10 stocks)
# =============================================================================
stocks.extend([
    make_stock(
        'tata-steel', 'Tata Steel Limited', 'TATASTEEL',
        'Large-Cap Integrated Steel Producer', 'High', 6, 152.0, '3 - 5 Years',
        '13.5% - 17.0% CAGR', '5Y Historical CAGR',
        'Global steel major with lowest-cost captive iron ore mines in India, expanding domestic crude steel capacity to 40 MTPA while restructuring UK green steel operations with government support.',
        'Indian infrastructure steel demand, captive raw material cost moat, Kalinganagar expansion, and European de-risking.',
        ['100% captive iron ore integration in India delivering structurally superior domestic EBITDA per tonne (~Rs 15,000+)', 'Massive 5 MTPA Kalinganagar phase-2 expansion ramping up high-margin value-added flat steels', 'UK Port Talbot restructuring with UK government grant transitioning to low-emission Electric Arc Furnace (EAF)'],
        ['Global steel price cycles heavily influenced by Chinese property sector demand and steel exports', 'European operational restructuring involves transitional severance and shutdown charges', 'High cyclical beta characteristic of commodity steel equities']
    ),
    make_stock(
        'jsw-steel', 'JSW Steel Limited', 'JSWSTEEL',
        'Large-Cap Integrated Steel Producer', 'High', 6, 960.0, '3 - 5 Years',
        '14.0% - 17.5% CAGR', '5Y Historical CAGR',
        'Flagship company of the JSW Group and India’s largest private steel producer, scaling capacity toward 50 MTPA with world-class plant conversion efficiency and value-added steel leadership.',
        'Aggressive domestic steel volume expansion, Vijayanagar brownfield ramp-up, and automotive high-tensile steel leadership.',
        ['Industry-benchmark project execution speed and lowest capital cost per tonne of steel plant capacity build-out', 'High proportion (> 60%) of value-added and special products insulating against commoditized steel price dumps', 'Strong domestic automotive steel market share through strategic partnership with JFE Steel Japan'],
        ['High dependency on purchased iron ore and imported coking coal compared to Tata Steel’s captive mines', 'High absolute financial debt incurred to fund continuous large-scale brownfield steel expansions', 'Vulnerability to global steel trade dumping and raw material price spikes']
    ),
    make_stock(
        'hindalco-industries', 'Hindalco Industries Limited', 'HINDALCO',
        'Large-Cap Aluminium & Copper Major', 'High', 6, 680.0, '3 - 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR',
        'World’s largest aluminum rolling company (Noveliss) and major copper producer, dominating beverage can recycling, automotive lightweighting, and domestic smelting.',
        'Global beverage can packaging demand, EV automotive aluminum lightweighting, Bay Minette US plant expansion, and domestic copper demand.',
        ['Novelis is the undisputed global leader in recycled beverage can sheet and automotive structural aluminum', 'Low-cost domestic upstream aluminum smelting supported by captive coal and bauxite linkages', 'Massive free cash flow generation enabling sustained balance sheet deleveraging (Net Debt to EBITDA < 1.5x)'],
        ['London Metal Exchange (LME) aluminum commodity spot price cyclicality', 'High capital expenditure in Novelis’ greenfield Bay Minette rolling facility in the US', 'Global trade tariffs and carbon border adjustment mechanisms (CBAM) in Europe']
    ),
    make_stock(
        'vedanta', 'Vedanta Limited', 'VEDL',
        'Large-Cap Natural Resources Major', 'High', 7, 480.0, '3 - 5 Years',
        '14.0% - 18.0% CAGR', '5Y Historical CAGR',
        'Diversified natural resources conglomerate with world-class low-cost operations in zinc (Hindustan Zinc), aluminum, oil & gas (Cairn), and iron ore, delivering high dividend yields.',
        'Low-cost zinc and aluminum smelting, proposed structural demerger into pure-play entities, and record dividend payouts.',
        ['Lowest quartile cost of production globally in zinc smelting through 65% stake in Hindustan Zinc', 'High historical dividend yield (> 8%) returning substantial operating cash flows to shareholders', 'Comprehensive presence across strategic base metals essential for national industrialization'],
        ['High debt levels at the parent holding company (Vedanta Resources) creating ongoing refinancing scrutiny', 'Cyclical commodity price volatility across zinc, aluminum, and crude oil realizations', 'Environmental and regulatory scrutiny on mining and smelting operational sites']
    ),
    make_stock(
        'national-aluminium', 'National Aluminium Company Limited (NALCO)', 'NATIONALUM',
        'Mid-Cap Integrated Aluminium PSU', 'High', 7, 220.0, '3 - 5 Years',
        '14.0% - 18.5% CAGR', '5Y Historical CAGR',
        'Navratna PSU operating one of the world’s lowest-cost bauxite mines and alumina refineries at Panchpatmali, with captive coal mines (Pottangi, Utkal D/E) securing long-term cost leadership.',
        'High alumina global export prices, captive coal operationalization, and aluminum smelter brownfield expansion.',
        ['Among the lowest-cost producers of metallurgical grade alumina globally owing to high-quality captive bauxite mines', 'Pristine debt-free balance sheet with high cash reserves and regular attractive dividend yields (~4.5%)', 'Direct beneficiary of high international alumina contract premiums on global commodity markets'],
        ['Single-region geographic concentration of mining and smelting operations in Odisha', 'High sensitivity of net earnings to London Metal Exchange (LME) aluminum spot price swings', 'Public sector ownership and sovereign dividend expectations']
    ),
    make_stock(
        'nmdc', 'NMDC Limited', 'NMDC',
        'Large-Cap Iron Ore Mining PSU', 'Medium', 5, 230.0, '3 - 5 Years',
        '13.0% - 16.0% CAGR', '5Y Historical CAGR',
        'India’s single largest iron ore producer accounting for over 20% of national output, operating highly mechanized mines in Chhattisgarh and Karnataka with massive reserves.',
        'Record steel production volumes in India driving iron ore consumption, slurry pipeline commissioning, and high dividend payouts.',
        ['Monopoly scale in high-grade merchant iron ore with over 45 MTPA output targeting 67 MTPA by 2026', 'Debt-free balance sheet generating strong operating cash flows and consistent dividend yields (~4.5%)', 'Strategic key supplier to major blast furnaces across public and private Indian steel mills'],
        ['Domestic iron ore price realizations are sensitive to global iron ore index swings and steel production curbs', 'Mining royalty hikes by state governments (Chhattisgarh, Karnataka) and forest clearance reviews', 'Cyclical stock price fluctuations characteristic of pure-play commodity miners']
    ),
    make_stock(
        'ultratech-cement', 'UltraTech Cement Limited', 'ULTRACEMCO',
        'Large-Cap Cement Manufacturing Leader', 'Medium', 5, 11250.0, '> 5 Years',
        '13.5% - 16.5% CAGR', '5Y Historical CAGR',
        'Flagship company of the Aditya Birla Group and India’s undisputed cement titan with over 150 MTPA capacity, ranking as the 3rd largest cement company globally outside China.',
        'National highway infrastructure, affordable housing, smart city projects, and strategic capacity acquisitions (Kesoram, India Cements).',
        ['Unrivalled pan-India manufacturing and grinding footprint commanding over 22% national cement market share', 'Exceptional supply chain efficiencies and lead-distance optimization minimizing logistics freight costs', 'Consistently profitable with high return on capital (RoCE > 16%) and strong investment grade balance sheet'],
        ['Intense regional price competition and consolidation battles with the Adani Cement group', 'Fuel cost volatility in petcoke, imported thermal coal, and diesel freight tariffs', 'Direct equity market risks during real estate and construction slow-downs']
    ),
    make_stock(
        'grasim-industries', 'Grasim Industries Limited', 'GRASIM',
        'Large-Cap Industrial & Consumer Paints Conglomerate', 'Medium', 5, 2620.0, '> 5 Years',
        '14.0% - 17.0% CAGR', '5Y Historical CAGR',
        'Flagship Aditya Birla conglomerate dominating Viscose Staple Fibre (VSF) and Chlor-Alkali, disrupting Indian decorative coatings with mega Rs 10,000 Crore Birla Opus paints rollout.',
        'Birla Opus decorative paints pan-India market share capture, VSF textile recovery, and holding value in UltraTech Cement and Aditya Birla Capital.',
        ['Global leadership in Viscose Staple Fibre and India’s largest caustic soda chlor-alkali producer', 'Disruptive Birla Opus paint launch targeting #2 industry spot with state-of-the-art automated mega plants', 'Deep value anchor through controlling 57% equity stake in India’s cement leader UltraTech Cement'],
        ['Gestational operating losses in the aggressive initial marketing and dealer acquisition of Birla Opus paints', 'Holding company discount on listed equity investments (UltraTech Cement, AB Capital)', 'Global cyclicality in textile fiber demand and international caustic soda prices']
    ),
    make_stock(
        'ambuja-cements', 'Ambuja Cements Limited', 'AMBUJACEM',
        'Large-Cap Cement Producer', 'Medium', 5, 570.0, '> 5 Years',
        '13.5% - 16.5% CAGR', '5Y Historical CAGR',
        'Major cement producer of the Adani Group, operating alongside ACC with aggressive capacity expansion targeting 140 MTPA by 2028, backed by massive cash reserves.',
        'Accelerating plant capacity expansions, green power captive adoption, captive railway logistics, and Sanghi/Penna cement acquisitions.',
        ['Debt-free balance sheet with massive cash reserves exceeding Rs 15,000 Crore funding organic and inorganic capex', 'Synergies with Adani Group ports, logistics, power, and railway infrastructure significantly lowering operating costs', 'High brand equity and contractor loyalty across northern, western, and eastern regional markets'],
        ['Intense price wars and volume competition with market leader UltraTech Cement', 'Raw material input cost inflation in limestone royalties, gypsum, and power tariffs', 'Stock market risk typical of large-cap manufacturing and industrial equities']
    ),
    make_stock(
        'shree-cement', 'Shree Cement Limited', 'SHREECEM',
        'Large-Cap Cost-Efficient Cement Producer', 'Medium', 5, 24800.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'One of India’s most efficient and lowest-cost cement manufacturers, pioneering green power captive generation (waste heat recovery WHRS) and synthetic gypsum.',
        'Cost-leadership expansion across Northern, Eastern, and Southern cement markets, alongside high green power share (> 55%).',
        ['Industry-lowest power and fuel costs per tonne driven by early adoption of Waste Heat Recovery Systems', 'Conservative debt-free balance sheet with strong return on invested capital through multiple cycles', 'Consistent organic capacity expansion funded entirely through internal cash accruals'],
        ['Historically lower presence in high-growth southern and western markets, which it is currently expanding into', 'Regional cement price volatility in northern and eastern clusters', 'High nominal stock price per share creates perception barrier for retail investors']
    )
])

# =============================================================================
# I. Infrastructure and Real Estate (8 stocks)
# =============================================================================
stocks.extend([
    make_stock(
        'dlf', 'DLF Limited', 'DLF',
        'Large-Cap Luxury Real Estate Developer', 'High', 7, 830.0, '3 - 5 Years',
        '15.0% - 18.5% CAGR', '5Y Historical CAGR',
        'India’s largest listed real estate developer dominating Gurugram luxury housing (The Camellias, The Arbour) and holding massive Grade-A rental office portfolio (DCCDL joint venture with GIC).',
        'Record luxury residential sales velocity, mega launch pipeline in NCR, Mumbai, and Goa, and growing rental income from Grade-A commercial cyber cities.',
        ['Unrivalled land bank in prime micro-markets of Gurugram with fully paid-up low historical acquisition cost', 'Residential business is completely net-debt-free with record multi-thousand-crore project sellouts within hours', 'DCCDL office rental portfolio generates steady, inflation-hedged annual rental cash flows (> Rs 4,500 Crore)'],
        ['Real estate is inherently cyclical and sensitive to interest rate hikes and luxury buyer sentiment', 'Geographic concentration of residential project launches in the Delhi-NCR and Gurugram markets', 'Stock price beta is elevated during macroeconomic and monetary tightening cycles']
    ),
    make_stock(
        'godrej-properties', 'Godrej Properties Limited', 'GODREJPROP',
        'Large-Cap Pan-India Real Estate Developer', 'High', 7, 2950.0, '3 - 5 Years',
        '16.0% - 20.0% CAGR', '5Y Historical CAGR',
        'Real estate arm of the Godrej Group and India’s leading residential developer by booking value, executing prime residential developments across Mumbai, NCR, Bengaluru, and Pune.',
        'Pan-India geographic diversification, aggressive land acquisitions via outright purchase and JVs, and trusted corporate governance.',
        ['Market leader in total residential booking value exceeding Rs 20,000 Crore annually', 'Highest consumer trust and brand recall in Indian real estate backed by the 127-year Godrej legacy', 'True pan-India presence diversifying project execution across Mumbai, Delhi-NCR, Bengaluru, and Pune'],
        ['Cash flow timing mismatch: substantial upfront capital deployed into outright land purchases before project collections', 'Execution and construction delivery velocity risks across dozens of simultaneous active project sites', 'High valuation multiples make the stock volatile during broader market pullbacks']
    ),
    make_stock(
        'prestige-estates', 'Prestige Estates Projects Limited', 'PRESTIGE',
        'Large-Cap Diversified Real Estate Developer', 'High', 7, 1750.0, '3 - 5 Years',
        '15.5% - 19.5% CAGR', '5Y Historical CAGR',
        'Premier South Indian real estate developer expanding aggressively into Mumbai, Delhi-NCR, and Hyderabad, commanding diversified operations across residential, commercial offices, malls, and hospitality.',
        'High-velocity residential pre-sales, commercial office completions in Bengaluru and Mumbai, and proposed hospitality REIT listing.',
        ['Dominant market leadership in Bengaluru real estate with expanding footprints in Mumbai and Hyderabad', 'Diversified revenue model combining residential sales with annuity rental office and mall assets', 'Strong pipeline of commercial office and hotel projects delivering future asset monetization'],
        ['Higher financial leverage incurred to fund simultaneous multi-city land acquisitions and commercial construction', 'Commercial office space leasing velocity sensitive to IT services corporate hiring and work-from-home trends', 'Higher beta characteristic of real estate expansion equities']
    ),
    make_stock(
        'lodha-developers', 'Macrotech Developers Limited (Lodha)', 'LODHA',
        'Large-Cap Residential Real Estate Leader', 'High', 7, 1180.0, '3 - 5 Years',
        '15.5% - 19.0% CAGR', '5Y Historical CAGR',
        'India’s largest residential real estate developer by sales bookings, dominating the Mumbai Metropolitan Region (MMR) and expanding rapidly through capital-light joint development agreements (JDAs) into Pune and Bengaluru.',
        'MMR residential leadership, digital logistics industrial park monetization, and capital-light asset-light JDA expansion.',
        ['Dominant market share (> 10%) in India’s most lucrative real estate market: Mumbai Metropolitan Region', 'Remarkable balance sheet transformation achieving near net-zero debt through disciplined cash collections', 'Unique township land parcel at Palava providing long-term low-cost industrial and residential land monetization'],
        ['High geographic concentration of active revenues in the Mumbai Metropolitan Region', 'Sensitivity to municipal approval timelines and local state real estate stamp duty policy changes', 'Equity volatility during interest rate upcycles']
    ),
    make_stock(
        'irfc', 'Indian Railway Finance Corporation', 'IRFC',
        'Large-Cap Sovereign Railway NBFC', 'Medium', 5, 155.0, '> 5 Years',
        '13.0% - 16.0% CAGR', '5Y Historical CAGR',
        'Dedicated market borrowing arm of the Ministry of Railways, financing rolling stock (locomotives, passenger coaches, freight wagons) and national railway infrastructure projects on a cost-plus lease model.',
        'Indian Railways multi-lakh-crore infrastructure modernization, dedicated freight corridors, Vande Bharat train additions, and high dividend payouts.',
        ['Zero non-performing assets (Gross NPA = 0%) due to 100% sovereign exposure to Ministry of Railways', 'Cost-plus regulated margin leasing model guarantees positive net interest margins on all deployed capital', 'Exceptional credit rating (AAA / Sovereign equivalent) ensuring lowest borrowing costs in domestic and international markets'],
        ['Net interest margins are capped by contractual agreement with the Ministry of Railways', 'Stock price experienced substantial re-rating, elevating sensitivity to government capex budgetary allocations', 'Dividend payouts and capital structure subject to Department of Investment and Public Asset Management (DIPAM) mandates']
    ),
    make_stock(
        'rvnl', 'Rail Vikas Nigam Limited', 'RVNL',
        'Mid/Large-Cap Railway EPC PSU', 'High', 7, 440.0, '3 - 5 Years',
        '15.0% - 19.0% CAGR', '5Y Historical CAGR',
        'Executing arm of Indian Railways for fast-track infrastructure projects: new rail lines, doubling, gauge conversion, railway electrification, metro projects, and Vande Bharat trainset manufacturing.',
        'High-speed rail corridor execution, metro rail EPC bidding, international overseas rail projects, and Vande Bharat manufacturing JV.',
        ['Robust order book exceeding Rs 85,000 Crore providing high multi-year revenue visibility', 'Diversifying into non-railway infrastructure: domestic metro systems, highways, and overseas railway construction (Maldives, Uzbekistan)', 'Asset-light project management consultancy model ensuring low capital intensity and zero long-term debt'],
        ['Low operating EBITDA margins (~6%) typical of competitive infrastructure construction contractors', 'Project execution delays caused by land acquisition, terrain tunneling challenges, and climatic conditions', 'High stock price beta following historic run-up elevates drawdown risk during market consolidations']
    ),
    make_stock(
        'ircon-international', 'IRCON International Limited', 'IRCON',
        'Mid-Cap Transport Infrastructure PSU', 'High', 7, 215.0, '3 - 5 Years',
        '14.0% - 17.5% CAGR', '5Y Historical CAGR',
        'Specialized engineering and construction PSU with deep expertise in difficult railway terrain, high-altitude tunneling (Jammu-Kashmir rail link), highways, and international turnkey projects.',
        'Complex railway construction projects, national highway hybrid annuity model (HAM) execution, and international rail projects.',
        ['Pristine reputation for executing technologically complex rail projects in difficult mountainous and seismic terrains', 'Debt-free balance sheet with solid cash balance and attractive regular dividend yields (~3.5%)', 'Expanding highway and high-speed rail order book reducing sole dependency on traditional railway lines'],
        ['Construction margin vulnerability to input raw material cost spikes in fixed-rate contracts', 'Lumpy billing cycles dependent on state government infrastructure milestone certifications', 'Stock price sensitivity to public sector construction budget execution trends']
    ),
    make_stock(
        'concor', 'Container Corporation of India', 'CONCOR',
        'Large-Cap Multimodal Logistics PSU', 'Medium', 5, 860.0, '> 5 Years',
        '13.5% - 16.5% CAGR', '5Y Historical CAGR',
        'Pioneer and market leader in containerized rail freight logistics in India, operating over 60 Inland Container Depots (ICDs) and direct rail connectivity to major maritime gateway ports.',
        'Western Dedicated Freight Corridor (DFC) operationalization, modal shift from road to rail container freight, and strategic PSU divestment potential.',
        ['Dominant domestic market share (~65%) in containerized rail freight with unmatched network of inland dry ports', 'Direct beneficiary of Western DFC enabling double-stack container trains with significantly faster turnaround times', 'Strong balance sheet with minimal debt and consistent dividend payouts'],
        ['High Land License Fee (LLF) paid to Indian Railways for operating ICDs on railway land', 'Competition from private container train operators and trucking transport fleets on short-haul routes', 'Sensitivity to international trade merchandise export-import (EXIM) volume cycles']
    )
])

print(f"Added all sectors! Total stocks: {len(stocks)}")

# Save complete stocks catalogue
stocks_path = os.path.join(root_dir, 'app', 'services', 'catalogue', 'stocks.py')
with open(stocks_path, 'w', encoding='utf-8') as f:
    f.write('"""\nExpanded Indian Stocks Catalogue across 9 Major Sectors for MoneyLeak.\n')
    f.write('Covering Banking, IT, Energy, Consumer, Autos, Healthcare, Telecom, Metals, and Infrastructure.\n"""\n')
    f.write('from typing import Dict, Any, List\n\n')
    f.write('STOCKS_CATALOGUE: List[Dict[str, Any]] = ')
    pprint.pprint(stocks, stream=f, indent=4, width=120)
    f.write('\n')

print(f"Successfully wrote {stocks_path} with {len(stocks)} stocks.")
