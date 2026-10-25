# -*- coding: utf-8 -*-
"""
Appends Sectors E (Automobiles & Manufacturing) and F (Pharma & Healthcare)
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
# E. Automobiles and Manufacturing (15 stocks)
# =============================================================================
stocks.extend([
    make_stock(
        'mahindra-and-mahindra', 'Mahindra & Mahindra Limited', 'M&M',
        'Large-Cap Automobile & Farm Equipment', 'Medium', 5, 2880.0, '> 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR',
        'India’s SUV market leader (Scorpio-N, Thar, XUV700) and world’s largest tractor manufacturer by volume, scaling electric SUVs and farm mechanization.',
        'Dominant premium SUV market leadership, tractor cycle recovery, and electric vehicle platform scale.',
        ['Commanding market share in high-margin authentic premium SUVs with massive order backlogs', 'Undisputed global leadership in agricultural tractors and farm machinery', 'Strong subsidiary ecosystem (Tech Mahindra, Mahindra Lifespaces, Mahindra Finance)'],
        ['Cyclical dependency of tractor division on monsoon rainfall and rural farm incomes', 'Aggressive competitive EV launches by global and domestic automotive rivals', 'Equity price beta during broader cyclical market corrections']
    ),
    make_stock(
        'maruti-suzuki', 'Maruti Suzuki India Limited', 'MARUTI',
        'Large-Cap Passenger Vehicles Leader', 'Medium', 5, 11950.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'India’s dominant passenger car manufacturer holding over 40% market share, with unmatched sales/service network (NEXA, Arena) and leading CNG vehicle penetration.',
        'SUV portfolio expansion (Grand Vitara, Brezza), hybrid technology leadership with Toyota, and rising export volumes.',
        ['Unrivalled distribution and service ecosystem present in virtually every Indian town and district', 'Dominant cost-leadership in affordable small cars and high-efficiency hybrid powertrains', 'Massive net cash balance sheet and high return on capital employed (RoCE > 20%)'],
        ['Slow initial rollout of pure battery electric vehicles relative to specialized EV peers', 'Regulatory emission compliance costs and safety mandate cost pressures on entry-level vehicles', 'Market risk during passenger vehicle demand slowdowns']
    ),
    make_stock(
        'tata-motors', 'Tata Motors Limited', 'TATAMOTORS',
        'Large-Cap Commercial & Electric Vehicles', 'High', 6, 890.0, '3 - 5 Years',
        '15.0% - 18.0% CAGR', '5Y Historical CAGR',
        'Pioneer of India’s electric car revolution (Nexon.ev, Punch.ev) and commercial vehicle market leader, commanding global luxury SUV giant Jaguar Land Rover.',
        'JLR order book execution, Indian commercial freight vehicle upcycle, and planned demerger into commercial and passenger businesses.',
        ['Over 70% market share in domestic Indian electric passenger vehicles', 'JLR order book is dominated by ultra-profitable luxury Range Rover, Defender, and Discovery models', 'Demerger into two pure-play listed entities unlocks focused capital allocation and value'],
        ['Commercial vehicle industry is inherently cyclical and sensitive to industrial GDP and freight rates', 'Global supply chain risks and geopolitical uncertainties affecting European luxury automotive sales', 'Higher debt and cash flow cyclicality compared to pure cash-rich domestic competitors']
    ),
    make_stock(
        'hyundai-motor-india', 'Hyundai Motor India Limited', 'HYUNDAI',
        'Large-Cap Passenger Vehicles', 'Medium', 5, 1820.0, '> 5 Years',
        '13.5% - 16.0% CAGR', '5Y Historical CAGR',
        'Second-largest passenger carmaker in India, renowned for feature-packed premium SUVs (Creta, Venue) and major export hub status from its Chennai and Talegaon plants.',
        'Compact and mid-size SUV market dominance, local EV manufacturing ramp-up, and export expansion.',
        ['Iconic brand recall with the best-selling mid-size SUV franchise in Indian history (Creta)', 'State-of-the-art flexible manufacturing with high operational efficiencies and high RoE', 'Strong export presence shipping made-in-India cars to over 80 countries globally'],
        ['Intense competitive rivalry in the SUV segment from Tata Motors, Mahindra, and Maruti', 'Royalty payments to South Korean parent company impacting net margins', 'Direct equity market risks typical of large-cap manufacturing stocks']
    ),
    make_stock(
        'bajaj-auto', 'Bajaj Auto Limited', 'BAJAJ-AUTO',
        'Large-Cap Two & Three Wheelers', 'Medium', 5, 9850.0, '> 5 Years',
        '14.0% - 16.5% CAGR', '5Y Historical CAGR',
        'World’s most valuable two-wheeler company, dominating premium motorcycles (Pulsar, KTM, Triumph), commercial 3-wheelers, and electric two-wheelers (Chetak).',
        'Premium motorcycle upgrades, expanding global exports across 70+ nations, and electric 3-wheeler adoption.',
        ['Uncontested global monopoly in commercial 3-wheelers delivering exceptionally high EBITDA margins', 'High-growth premium motorcycle alliance with Triumph (Speed 400) and KTM', 'Debt-free balance sheet generating massive free cash flows and regular high dividend payouts'],
        ['Export market sales sensitivity to US Dollar availability in African and Latin American economies', 'Rapid domestic electrification in two-wheelers pressuring internal combustion engine volumes', 'Equity market risk during automotive sector corrections']
    ),
    make_stock(
        'hero-motocorp', 'Hero MotoCorp Limited', 'HEROMOTOCO',
        'Large-Cap Two-Wheelers Leader', 'Medium', 5, 4850.0, '> 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR',
        'World’s largest manufacturer of motorcycles and scooters by unit volume, dominating rural and commuter India with iconic brands Splendor and HF Deluxe.',
        'Rural income revival, premium motorcycle expansion (Harley-Davidson X440, Mavrick), and VIDA EV rollout.',
        ['Unassailable brand dominance in entry-level 100cc-125cc motorcycles with Splendor', 'Deepest rural distribution network in India with over 6,000 dealerships and service points', 'Strong dividend yield (~3.5%) backed by zero debt and solid operating cash flows'],
        ['High dependency on the 100cc mass commuter segment which faces slower long-term growth', 'Intense competitive pressure in urban scooters and electric two-wheelers', 'Rural wage stagnation directly dampens entry-level two-wheeler replacement cycles']
    ),
    make_stock(
        'tvs-motor-company', 'TVS Motor Company Limited', 'TVSMOTOR',
        'Large-Cap Two & Three Wheelers', 'High', 6, 2480.0, '3 - 5 Years',
        '15.5% - 19.0% CAGR', '5Y Historical CAGR',
        'Technology-led two-wheeler manufacturer renowned for engineering excellence, leading in electric scooters (iQube), premium sport motorcycles (Apache), and BMW Motorrad manufacturing.',
        'Market share gains in domestic two-wheelers, rapid EV scooter volume scale, and European expansion via Norton Motorcycles.',
        ['Outperformed all two-wheeler peers in sustained domestic market share expansion over the past decade', 'Fast-growing EV scooter business (iQube) consistently ranking among India’s top 2 EV makers', 'Strategic technical collaboration with BMW Motorrad for sub-500cc global motorcycle production'],
        ['Lower operating margins historically than Bajaj Auto due to higher product promotion costs', 'Higher financial leverage to fund global overseas subsidiaries (Norton Motorcycles)', 'High valuation multiples make the stock sensitive to monthly volume growth metrics']
    ),
    make_stock(
        'eicher-motors', 'Eicher Motors Limited', 'EICHERMOT',
        'Large-Cap Premium Motorcycles & Commercial Vehicles', 'Medium', 5, 4820.0, '> 5 Years',
        '14.0% - 16.5% CAGR', '5Y Historical CAGR',
        'Parent company of Royal Enfield, dominating the mid-size leisure motorcycling segment (350cc-650cc) globally, alongside VECV commercial vehicles joint venture with Volvo Group.',
        'Global leisure motorcycling lifestyle culture, expanding 450cc/650cc twin platforms (Himalayan, Interceptor), and VECV truck upcycle.',
        ['Near-monopolistic domestic market share (> 85%) in premium 250cc-750cc middleweight motorcycles', 'Phenomenal brand loyalty and community cult following driving high gross profit margins (> 40%)', 'Profitable commercial vehicle partnership with Volvo Trucks scaling bus and medium-duty truck market share'],
        ['Rising competitive entry from global joint ventures (Triumph-Bajaj, Harley-Hero)', 'Leisure motorcycle demand vulnerable to urban consumer discretionary spend slowdowns', 'Stock price fluctuations typical of premium consumer cyclicals']
    ),
    make_stock(
        'ashok-leyland', 'Ashok Leyland Limited', 'ASHOKLEY',
        'Large-Cap Medium & Heavy Commercial Vehicles', 'High', 6, 215.0, '3 - 5 Years',
        '13.5% - 17.0% CAGR', '5Y Historical CAGR',
        'Flagship company of the Hinduja Group and India’s second-largest commercial vehicle manufacturer, commanding strong market share in trucks, buses, defense vehicles, and LCVs (Bada Dost).',
        'Infrastructure capex freight revival, bus fleet modernization by state transport undertakings, and defense logistics.',
        ['Robust positioning in medium and heavy commercial vehicles (M&HCV) benefiting from national highway freight expansion', 'Fast-growing light commercial vehicle (LCV) portfolio expanding non-cyclical revenue streams', 'Switch Mobility subsidiary scaling electric city bus and e-LCV fleets across major Indian metros'],
        ['Commercial vehicle sales are intensely cyclical, with sharp boom and bust demand swings', 'Steel, aluminium, and rubber raw material price volatility pressuring operating margins', 'Higher financial leverage during cyclical industry down-phases']
    ),
    make_stock(
        'bharat-electronics', 'Bharat Electronics Limited', 'BEL',
        'Large-Cap Defense Electronics PSU', 'Medium', 5, 295.0, '> 5 Years',
        '16.0% - 19.5% CAGR', '5Y Historical CAGR',
        'Premier defense electronics enterprise of the Government of India, manufacturing radars, missile electronic systems, naval sonar, avionics, and electronic warfare suites for the armed forces.',
        'Atmanirbhar Bharat defense indigenization, record multi-year order book (> Rs 75,000 Crore), and non-defense civilian scaling.',
        ['Near-monopoly status as the primary supplier of electronic mission-critical systems to the Indian Army, Navy, and Air Force', 'Massive order pipeline providing high multi-year revenue visibility with zero customer credit risk', 'Debt-free balance sheet delivering exceptional return on capital (RoCE > 30%) and solid dividends'],
        ['Single-customer dependency on the Indian Ministry of Defence for over 85% of order intake', 'Lumpy quarterly revenue recognition driven by defense delivery and testing milestone approvals', 'Stock price sensitivity to defense budget allocations and geopolitical news cycles']
    ),
    make_stock(
        'larsen-and-toubro', 'Larsen & Toubro Limited', 'LT',
        'Large-Cap Infrastructure & Engineering Conglomerate', 'Medium', 5, 3560.0, '> 5 Years',
        '14.0% - 16.5% CAGR', '5Y Historical CAGR',
        'India’s infrastructure titan executing mega EPC projects across transport, renewables, defense, hydrocarbons, and power, with a record order backlog exceeding Rs 5 Lakh Crore.',
        'National infrastructure modernization, Middle East hydrocarbon and green hydrogen capex, and IT/financial services subsidiaries.',
        ['Unmatched engineering scale and execution track record capable of handling multi-billion-dollar complex infrastructure projects', 'Massive international order wins in Saudi Arabia and the Middle East driving export revenue diversification', 'Substantial value contribution from listed IT subsidiaries (LTIMindtree, LTTS) and L&T Finance'],
        ['Fixed-price EPC contracts carry risk of margin compression if commodity raw material prices (steel, cement) spike', 'Working capital elongation and project execution delays due to land acquisition and environmental clearances', 'Market drawdowns apply during broader equity cyclical corrections']
    ),
    make_stock(
        'siemens-india', 'Siemens Limited', 'SIEMENS',
        'Large-Cap Industrial Automation & Electrification', 'High', 6, 7450.0, '3 - 5 Years',
        '15.5% - 18.5% CAGR', '5Y Historical CAGR',
        'Pioneer in industrial automation, digital enterprise software, smart grid transmission, and locomotive propulsion systems, driving India’s Industry 4.0 manufacturing revolution.',
        'Private capex revival, semiconductor factory automation, Indian Railways high-horsepower electric locomotive manufacturing, and green building efficiency.',
        ['German engineering excellence and market leadership in factory automation, digital enterprise, and smart energy infrastructure', 'Mega contract to supply and service 1,200 electric freight locomotives of 9,000 HP to Indian Railways', 'Decarbonization and energy efficiency solutions experiencing record industrial demand'],
        ['High valuation multiples reflect substantial growth optimism, elevating sensitivity to order inflow delays', 'Parent company demerger of energy business requires operational reorganization', 'Cyclical dependency on private sector industrial capital expenditure']
    ),
    make_stock(
        'abb-india', 'ABB India Limited', 'ABB',
        'Large-Cap Electrification & Robotics', 'High', 6, 7850.0, '3 - 5 Years',
        '15.0% - 18.5% CAGR', '5Y Historical CAGR',
        'Swiss-Swedish engineering leader specializing in electrification products, industrial robotics, energy-efficient electric motors, and process automation across manufacturing plants.',
        'Data center power distribution, green hydrogen electrolyzer automation, industrial robotics adoption, and energy-efficient motor standards.',
        ['Unrivalled technology leadership in robotics, electric drives, and medium-voltage smart electrification', 'Zero debt balance sheet with high cash generation and consistent RoCE (> 25%)', 'Direct beneficiary of India’s booming data center build-outs and electronics manufacturing plants'],
        ['Stock trades at premium valuation multiples that leave little margin for quarterly operational slips', 'Global supply chain lead times on specialized imported electronics components', 'Industrial capex cyclicality in heavy process industries']
    ),
    make_stock(
        'cummins-india', 'Cummins India Limited', 'CUMMINSIND',
        'Large-Cap Industrial Engines & Power Gensets', 'Medium', 5, 3580.0, '> 5 Years',
        '14.0% - 17.0% CAGR', '5Y Historical CAGR',
        'India’s leading manufacturer of medium and high-horsepower diesel and natural gas engines, standby generator sets for data centers and real estate, and rail propulsion systems.',
        'Surging data center standby power backup demand, CPCB IV+ emission norm price realisations, and hydrogen engine technologies.',
        ['Dominant market share in mission-critical backup power gensets for data centers, hospitals, and infrastructure projects', 'Successful transition to stringent CPCB IV+ emission standards driving substantial price realization increases', 'Strong engineering R&D center in Pune serving as a global engineering export hub for parent Cummins Inc.'],
        ['Stricter global decarbonization standards encourage long-term adoption of battery storage over diesel gensets', 'Raw material commodity price fluctuations (specialty steel, castings, copper)', 'Market risk during industrial manufacturing sector drawdowns']
    ),
    make_stock(
        'bharat-forge', 'Bharat Forge Limited', 'BHARATFORG',
        'Large-Cap Forgings & Advanced Engineering', 'High', 7, 1480.0, '3 - 5 Years',
        '15.5% - 19.0% CAGR', '5Y Historical CAGR',
        'Flagship company of the Kalyani Group and world’s largest forging company, expanding rapidly into indigenous defense artillery systems (ATAGS), aerospace components, and EV mobility.',
        'Defense artillery export orders, aerospace jet engine components, and North American commercial vehicle forging recovery.',
        ['World-class advanced metallurgy and forging scale supplying leading global automotive and aerospace OEMs', 'Breakthrough indigenous defense business: developed ATAGS 155mm artillery gun and armored vehicles winning major contracts', 'Diversification into non-automotive high-margin sectors (aerospace, defense, industrial equipment)'],
        ['Cyclical exposure to the North American Class 8 heavy truck production cycle', 'High capital expenditure in overseas aluminum forging facilities during ramp-up phase', 'Higher stock price beta during global manufacturing and trade slow-downs']
    )
])

# =============================================================================
# F. Pharmaceuticals and Healthcare (10 stocks)
# =============================================================================
stocks.extend([
    make_stock(
        'sun-pharmaceutical', 'Sun Pharmaceutical Industries Limited', 'SUNPHARMA',
        'Large-Cap Global Specialty Pharma', 'Medium', 5, 1880.0, '> 5 Years',
        '13.5% - 16.5% CAGR', '5Y Historical CAGR',
        'India’s largest pharmaceutical enterprise and world’s 4th largest specialty generics company, leading in dermatology, ophthalmology, and onco-dermatology global specialty drugs.',
        'High-margin global specialty pipeline (Ilumya, Cequa, Winlevi), domestic branded formulation leadership, and Taro acquisition completion.',
        ['Dominant domestic formulation market share (~8.5%) in chronic therapies generating steady cash flows', 'Global proprietary specialty portfolio generating over $1 Billion in high-margin recurring annual sales', 'Robust balance sheet with substantial net cash generating consistent free cash flows'],
        ['US FDA regulatory inspections and potential import alert compliance risks on manufacturing plants', 'Pricing pressures in generic commoditized oral solid formulations in the US market', 'Patent litigation and clinical trial risk on novel specialty pipeline molecules']
    ),
    make_stock(
        'dr-reddys-laboratories', 'Dr. Reddy’s Laboratories Limited', 'DRREDDY',
        'Large-Cap Generics & Biosimilars', 'Medium', 5, 6680.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'Global pharmaceutical major with strong presence in the US, Europe, Russia, and India, leading in complex generics, biosimilars, and active pharmaceutical ingredients (APIs).',
        'Complex generic launches, global biosimilar expansion, weight-loss GLP-1 generic development, and consumer health joint ventures (Nestlé JV).',
        ['Strong track record of launching first-to-market limited-competition complex generics in the US', 'Deep presence across emerging markets (Russia, CIS) providing geographic revenue diversification', 'Solid return on capital (RoCE > 22%) supported by strong cash conversion and clean balance sheet'],
        ['Revenue concentration in high-margin blockbuster generics (such as generic Revlimid) facing eventual patent expiry', 'US FDA inspection observations on API and formulation manufacturing facilities', 'Currency volatility in Russian Ruble and emerging market currencies']
    ),
    make_stock(
        'cipla', 'Cipla Limited', 'CIPLA',
        'Large-Cap Respiratory & Formulations Leader', 'Medium', 4, 1540.0, '> 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR',
        'Pharmaceutical pioneer renowned for global leadership in respiratory therapies (inhalers, nebulizers), dominating the domestic branded formulation market and South African private healthcare.',
        'Global respiratory leadership (generic Advair, Albuterol), domestic consumer healthcare (Cipla Health), and US complex peptide filings.',
        ['Global technological moat in inhalation and complex respiratory drug-device combination products', 'Top-3 ranking in Indian domestic branded formulations with high chronic therapy exposure', 'Strong presence in South Africa as the leading provider of affordable essential medicines'],
        ['Regulatory inspection outcomes at primary formulation facilities (Pithampur, Goa)', 'Intense competition in generic respiratory inhalers in North America', 'Direct equity market risk during healthcare sector rotations']
    ),
    make_stock(
        'divis-laboratories', 'Divi’s Laboratories Limited', 'DIVISLAB',
        'Large-Cap Active Pharmaceutical Ingredients (API) & CDMO', 'High', 6, 5890.0, '3 - 5 Years',
        '15.0% - 18.0% CAGR', '5Y Historical CAGR',
        'World’s leading manufacturer of active pharmaceutical ingredients (APIs) and customized custom synthesis (CDMO) for top global innovator pharmaceutical companies.',
        'Custom synthesis CDMO contracts for novel patent-protected innovator drugs, GLP-1 peptide building blocks, and greenfield Kakinada plant scaling.',
        ['Unrivalled global scale in core APIs (Naproxen, Dextromethorphan) commanding over 65% global market share', 'Trusted strategic CDMO partner to 12 of the world’s top 20 innovator pharmaceutical companies', 'Pristine debt-free balance sheet with industry-leading EBITDA margins (~30%)'],
        ['Lumpy quarterly custom synthesis revenue recognition depending on global innovator campaign runs', 'Raw material basic chemical cost inflation sourced from international chemical suppliers', 'Premium valuation multiples make the stock sensitive to quarterly earnings variability']
    ),
    make_stock(
        'lupin', 'Lupin Limited', 'LUPIN',
        'Large-Cap Generics & Complex Respiratory', 'High', 6, 2150.0, '3 - 5 Years',
        '14.0% - 17.5% CAGR', '5Y Historical CAGR',
        'Global pharmaceutical player recognized for rapid operating turnaround driven by complex respiratory launches (Spiriva generic), biosimilars, and strong Indian branded chronic formulations.',
        'Complex inhalation launches in the US, domestic Indian formulation expansion (cardiac, anti-diabetes), and biosimilar commercialization.',
        ['First-mover generic Spiriva commercialization generating substantial high-margin US cash flows', 'Turnaround in operating EBITDA margins from 10% toward 20%+', 'Top-tier domestic Indian formulation franchise with strong doctor prescription loyalty'],
        ['Competitive entry by other generic players into exclusive complex respiratory opportunities', 'US FDA regulatory inspection compliance across multiple manufacturing sites', 'Stock price beta is elevated during global generic pricing fluctuations']
    ),
    make_stock(
        'torrent-pharmaceuticals', 'Torrent Pharmaceuticals Limited', 'TORNTPHARM',
        'Large-Cap Chronic Branded Formulations', 'Medium', 5, 3250.0, '> 5 Years',
        '14.0% - 16.5% CAGR', '5Y Historical CAGR',
        'Specialty pharma major focused primarily on high-margin branded formulations in India, Brazil, and Germany, commanding market leadership in cardiovascular and CNS therapies.',
        'Domestic chronic therapy prescription dominance, Curatio derma acquisition synergies, and Brazilian branded expansion.',
        ['Highest exposure to domestic chronic and sub-chronic therapies (~75% of sales) ensuring predictable non-cyclical cash flows', 'Industry-leading gross margins (> 72%) reflecting branded prescription pricing power', 'Successful integration of strategic acquisitions (Unichem, Curatio Healthcare)'],
        ['Substantial financial debt incurred to fund large domestic brand acquisitions', 'Government price control regulations (NLEM) on essential cardiac and diabetes medicines', 'Equity price fluctuations driven by broader pharmaceutical sector sentiment']
    ),
    make_stock(
        'apollo-hospitals', 'Apollo Hospitals Enterprise Limited', 'APOLLOHOSP',
        'Large-Cap Integrated Healthcare & Pharmacies', 'Medium', 5, 7120.0, '> 5 Years',
        '15.0% - 18.0% CAGR', '5Y Historical CAGR',
        'India’s largest integrated healthcare conglomerate, operating over 10,000 hospital beds, nationwide 6,000+ retail pharmacies, diagnostic centers, and the Apollo 24/7 digital health app.',
        'Hospital bed capacity additions, expanding international medical tourism, and Apollo HealthCo pharmacy monetization.',
        ['Unrivalled brand equity in tertiary and quaternary hospital care across India', 'Massive omni-channel pharmacy retail network delivering high cash generation', 'Strategic external investment into Apollo HealthCo setting benchmark digital health valuation'],
        ['High capital expenditure intensity in expanding greenfield hospital beds in tier-1 metro hubs', 'Gestational operating losses in Apollo 24/7 digital platform customer acquisition', 'Medical talent attrition and rising doctor remuneration costs']
    ),
    make_stock(
        'max-healthcare-institute', 'Max Healthcare Institute Limited', 'MAXHEALTH',
        'Large-Cap Premium Quaternary Healthcare', 'High', 6, 1020.0, '3 - 5 Years',
        '16.0% - 19.5% CAGR', '5Y Historical CAGR',
        'Fastest-growing hospital chain in India with dominant cluster density in Delhi-NCR and Mumbai, commanding highest average revenue per occupied bed (ARPOB > Rs 75,000).',
        'Aggressive brownfield bed expansions doubling bed capacity, land acquisitions in Gurugram, and international medical tourism.',
        ['Industry-highest ARPOB driven by focus on complex quaternary care (oncology, cardiac, neuro, organ transplants)', 'Prime real estate hospital locations in affluent high-paying metropolitan catchments', 'Phenomenal operational turnaround delivering industry-leading EBITDA margins (~28%)'],
        ['Concentration of hospital facilities in the Delhi-NCR geographic region', 'Execution risks associated with doubling operational bed capacity over the next 4 years', 'Premium valuation multiples make the stock sensitive to quarterly occupancy fluctuations']
    ),
    make_stock(
        'fortis-healthcare', 'Fortis Healthcare Limited', 'FORTIS',
        'Large-Cap Tertiary Hospital Network', 'High', 6, 640.0, '3 - 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR',
        'Leading integrated healthcare provider backed by global hospital operator IHH Healthcare Berhad, operating 28 hospitals and holding controlling stake in Agilus Diagnostics.',
        'Bed occupancy ramp-up, brownfield expansion, Agilus Diagnostics turnaround, and medical value travel.',
        ['Backing and governance of world-class healthcare operator IHH Healthcare Berhad', 'Flagship hospitals in premier urban micro-markets (Gurugram, Mumbai, Bengaluru, Kolkata)', 'High-margin diagnostics subsidiary (Agilus) offering complementary pathology network'],
        ['Historical legal overhangs related to the open offer by IHH Healthcare in Indian courts', 'Intense competitive hospital additions across key metropolitan healthcare clusters', 'Equity market volatility typical of healthcare turnaround stories']
    ),
    make_stock(
        'zydus-lifesciences', 'Zydus Lifesciences Limited', 'ZYDUSLIFE',
        'Large-Cap Formations & Biosimilars', 'High', 6, 1010.0, '3 - 5 Years',
        '14.0% - 17.0% CAGR', '5Y Historical CAGR',
        'Innovative healthcare enterprise with strong US generics presence, growing domestic consumer wellness business (Zydus Wellness), and proprietary novel molecules (Saroglitazar).',
        'US specialty filings (Asacol generic, oncology), domestic chronic formulations, and New Chemical Entity (NCE) clinical commercialization.',
        ['Strong cash flows from lucrative limited-competition complex generics in North America', 'Pioneering proprietary drug discovery program with approved NCE molecule Saroglitazar for liver diseases', 'Debt-free balance sheet with robust return on equity (RoE ~20%)'],
        ['High dependency on select blockbuster US generic product revenues facing eventual competition', 'Regulatory scrutiny and US FDA inspection observations on formulation facilities', 'Stock price sensitivity to quarterly US generic price erosion trends']
    )
])

print(f"Added Sectors E & F. Total stocks: {len(stocks)}")

# Save intermediate progress
stocks_path = os.path.join(root_dir, 'app', 'services', 'catalogue', 'stocks.py')
with open(stocks_path, 'w', encoding='utf-8') as f:
    f.write('"""\nExpanded Indian Stocks Catalogue across 9 Major Sectors for MoneyLeak.\n"""\n')
    f.write('from typing import Dict, Any, List\n\n')
    f.write('STOCKS_CATALOGUE: List[Dict[str, Any]] = ')
    pprint.pprint(stocks, stream=f, indent=4, width=120)
    f.write('\n')

print(f"Saved {len(stocks)} stocks.")
