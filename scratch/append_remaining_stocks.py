# -*- coding: utf-8 -*-
"""
Appends Sectors C, D, E, F, G, H, I to app/services/catalogue/stocks.py
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
# C. Energy, Power and Utilities (12 stocks)
# =============================================================================
stocks.extend([
    make_stock(
        'reliance-industries', 'Reliance Industries Limited', 'RELIANCE',
        'Large-Cap Energy & Telecom Conglomerate', 'Medium', 5, 2870.0, '> 5 Years',
        '13.5% - 16.5% CAGR', '5Y Historical CAGR',
        'India’s most valuable enterprise, spanning global-scale oil-to-chemicals refining, digital services (Jio 5G), retail supermarkets, and massive green energy giga-factories.',
        'Compounding across India’s digital data consumption, organized retail expansion, and clean energy transition.',
        ['Market leader in telecom (Jio 480M subscribers) and organized retail (Reliance Retail 18,000 stores)', 'World-class integrated refining and petrochemical assets generating massive operating cash flows', 'Multi-billion dollar clean energy investments in solar, green hydrogen, and battery storage'],
        ['Large capital expenditure cycles in telecom 5G and green energy may compress return ratios in intermediate term', 'Exposure to global crude oil refining margins and petrochemical crack spreads', 'Market drawdowns apply during broader equity corrections']
    ),
    make_stock(
        'ntpc', 'NTPC Limited', 'NTPC',
        'Large-Cap Power Generation Utility', 'Medium', 4, 410.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'India’s largest power producer accounting for 25% of national electricity generation, transitioning rapidly into renewable green energy (NTPC Green Energy).',
        'National baseload electricity demand growth, regulated return-on-equity model (CERC), and massive 60GW green energy pipeline.',
        ['Regulated utility business model guarantees 15.5% post-tax return on equity on capitalized power plants', 'Sovereign majority ownership and secure power purchase agreements (PPAs) with state discoms', 'Massive renewable expansion targeting 60 GW clean energy capacity by 2032 with NTPC Green IPO monetization'],
        ['State electricity distribution company (Discom) payment delays and financial health risks', 'Coal supply logistics and thermal plant environmental emission compliance costs', 'Capital allocation execution risk in massive solar and wind build-outs']
    ),
    make_stock(
        'power-grid-corporation', 'Power Grid Corporation of India', 'POWERGRID',
        'Large-Cap Power Transmission Utility', 'Medium', 4, 325.0, '> 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR',
        'Central transmission utility transmitting over 85% of India’s inter-regional electricity, delivering defensive regulated returns and high dividend yields.',
        'National grid evacuation for renewable energy corridors, smart grid smart metering, and high dividend cash flows.',
        ['Natural monopoly in high-voltage inter-state electricity transmission with zero direct volume risk', 'Cost-plus regulated CERC model guaranteeing steady post-tax 15.5% return on equity', 'Consistently high dividend payout ratio (~60% of profits) generating attractive yields (~4%)'],
        ['Transmission project execution delays due to right-of-way (RoW) and forest clearance approvals', 'Increased bidding competition under Tariff-Based Competitive Bidding (TBCB) framework', 'Interest rate sensitivity on project debt refinancing']
    ),
    make_stock(
        'tata-power', 'Tata Power Company Limited', 'TATAPOWER',
        'Large-Cap Integrated Power & Clean Energy', 'High', 6, 425.0, '3 - 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR',
        'Pioneering integrated power company leading in solar EPC, rooftop solar (PM Surya Ghar), EV charging infrastructure, and transmission distribution.',
        'Rooftop solar adoption, utility-scale renewable generation, EV charging corridors, and distribution privatization.',
        ['Fully integrated utility model across renewable generation, transmission, and Odisha/Delhi distribution', 'Dominant market share in residential rooftop solar installations across India', 'Aggressive phase-out of thermal carbon footprint targeting net-zero emissions by 2045'],
        ['Legacy Mundra thermal plant fuel cost under-recovery and regulatory disputes', 'High execution competition in solar manufacturing and utility EPC margins', 'Equity market volatility during power sector cyclical pullbacks']
    ),
    make_stock(
        'adani-power', 'Adani Power Limited', 'ADANIPOWER',
        'Large-Cap Thermal Power Producer', 'High', 8, 610.0, '3 - 5 Years',
        '14.0% - 18.0% CAGR', '5Y Historical CAGR',
        'India’s largest private thermal power producer with over 15 GW operational capacity, expanding baseload power generation to meet India’s surging industrial electricity demand.',
        'Surging peak power deficits, merchant power realization tariffs, and power plant acquisition turnaround.',
        ['Massive operational thermal capacity benefiting from India’s record peak summer electricity demand', 'Secured long-term domestic coal linkages and dedicated pithead power plants', 'Turnaround in cash collections following regulatory resolution of past compensatory tariff claims'],
        ['High financial leverage and sensitivity to corporate group governance sentiment', 'Merchant electricity spot prices on power exchanges are volatile and weather-dependent', 'Higher stock price beta and drawdown risks during broader market corrections']
    ),
    make_stock(
        'coal-india', 'Coal India Limited', 'COALINDIA',
        'Large-Cap Mining PSU', 'Medium', 5, 480.0, '3 - 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR',
        'World’s largest coal mining company accounting for over 80% of India’s domestic coal production, generating massive cash flows and high dividend yields.',
        'Power sector fuel security, non-power industrial coal demand, e-auction premium realizations, and high dividend payouts.',
        ['Uncontested monopoly supplying over 80% of India’s thermal power station fuel requirements', 'Debt-free balance sheet with robust free cash flow and regular high dividend yield (~5.5% - 7%)', 'Increasing mechanized continuous miners and first-mile connectivity rail corridors boosting dispatch efficiency'],
        ['Global decarbonization policies and long-term coal phase-down energy transition risks', 'Regulated notified coal prices limit complete commercial price realization', 'Environmental clearance and labor union wage hike considerations']
    ),
    make_stock(
        'ongc', 'Oil and Natural Gas Corporation', 'ONGC',
        'Large-Cap Upstream Oil & Gas PSU', 'Medium', 5, 275.0, '3 - 5 Years',
        '12.0% - 15.0% CAGR', '5Y Historical CAGR',
        'India’s national upstream flagship producing 70% of domestic crude oil and 84% of natural gas, with offshore deepwater exploration in KG-DWN-98/2.',
        'Domestic hydrocarbon production revival, APM gas pricing floor, and subsidiary monetization (HPCL, MRPL, ONGC Videsh).',
        ['Critical national strategic asset providing sovereign energy security with vast proven hydrocarbon reserves', 'Domestic gas pricing reform establishes profitable floor price protecting upstream realization margins', 'Consistent high dividend payouts supported by strong cash generation during supportive crude oil cycles'],
        ['Sensitivity of crude oil realizations to global Brent commodity price shocks and geopolitical shifts', 'High capex intensity and geological exploration risk in ultra-deepwater offshore drilling', 'Government windfall taxes during periods of exceptionally elevated global crude prices']
    ),
    make_stock(
        'indian-oil-corporation', 'Indian Oil Corporation Limited', 'IOC',
        'Large-Cap Downstream Refining & Marketing', 'Medium', 5, 145.0, '3 - 5 Years',
        '12.0% - 14.5% CAGR', '5Y Historical CAGR',
        'India’s largest oil marketing company with over 36,000 retail fuel stations, extensive pipeline network, and major refining capacity.',
        'Automotive fuel consumption, petrochemical capacity additions, aviation turbine fuel demand, and dividend yields.',
        ['Dominant domestic retail fuel distribution market share exceeding 40%', 'Extensive nationwide pipeline network of over 17,000 km ensuring low-cost product transport', 'Attractive regular dividend payout track record'],
        ['Government retail fuel price freezes during election or high crude cost periods pressuring marketing margins', 'Cyclical volatility in Gross Refining Margins (GRMs) driven by global refining capacities', 'High working capital debt fluctuations tied to international crude inventory costs']
    ),
    make_stock(
        'bharat-petroleum', 'Bharat Petroleum Corporation Limited', 'BPCL',
        'Large-Cap Downstream Refining & Marketing', 'Medium', 5, 310.0, '3 - 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR',
        'Major oil marketing company operating highly complex refineries in Mumbai, Kochi, and Bina, leading in high-margin city gas distribution and non-fuel retail.',
        'Fuel retail volume growth, petrochemical expansion at Kochi and Bina, and electric vehicle charging hub rollouts.',
        ['High Nelson Complexity index refineries producing high proportions of value-added light distillates', 'Strong urban fuel retail network commanding high throughput per outlet', 'Substantial investments in renewable green hydrogen and petrochemical integration'],
        ['Retail fuel price realization constraints during elevated crude oil cost periods', 'Refining margin cyclicality and crude freight cost spikes', 'Market beta typical of public sector downstream energy companies']
    ),
    make_stock(
        'hindustan-petroleum', 'Hindustan Petroleum Corporation Limited', 'HINDPETRO',
        'Large-Cap Downstream Refining & Marketing', 'High', 6, 375.0, '3 - 5 Years',
        '12.5% - 15.5% CAGR', '5Y Historical CAGR',
        'Leading oil refining and marketing company (subsidiary of ONGC), completing major capacity expansion at Visakhapatnam and Rajasthan Barmer refinery.',
        'Visakhapatnam refinery modernization, retail fuel network expansion, and lube market leadership (HP Lubricants).',
        ['Significant refinery capacity expansion doubling processing capacity and boosting gross refining margins', 'Market leader in branded industrial and automotive lubricants (Club HP)', 'Extensive LPG domestic cooking gas distribution network serving millions of households'],
        ['Historically lower refining self-sufficiency than IOC and BPCL, making it more vulnerable to marketing margin squeezes', 'High working capital sensitivity to crude oil price swings', 'Stock price displays higher beta and earnings volatility during crude market shocks']
    ),
    make_stock(
        'gail-india', 'GAIL (India) Limited', 'GAIL',
        'Large-Cap Natural Gas Transmission', 'Medium', 5, 205.0, '3 - 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'India’s dominant natural gas transmission and marketing PSU, operating over 16,000 km of cross-country gas pipelines and major petrochemical plants.',
        'National transition to a gas-based economy (aiming for 15% gas in energy mix), city gas distribution expansions, and unified pipeline tariffs.',
        ['Monopoly in national natural gas transmission transmitting over 70% of India’s piped natural gas', 'Unified pipeline tariff implementation boosts transmission volumes across eastern and southern grids', 'Extensive city gas distribution (CGD) equity stakes spanning major metropolitan networks'],
        ['Petrochemical segment earnings vulnerable to global polymer price cycles and feedstock costs', 'US Henry Hub and global LNG long-term contract price arbitrage risks', 'Public sector ownership and sovereign dividend expectations']
    ),
    make_stock(
        'jsw-energy', 'JSW Energy Limited', 'JSWENERGY',
        'Large-Cap Renewable & Thermal Power', 'High', 7, 690.0, '3 - 5 Years',
        '15.5% - 19.0% CAGR', '5Y Historical CAGR',
        'Power producer of the JSW Group aggressively scaling green renewable capacity (solar, wind, and pumped hydro storage) aiming for 20 GW capacity by 2030.',
        'Rapid renewable capacity commissioning, commercial merchant power sales, and energy storage systems (ESS).',
        ['Aggressive green energy transformation with locked-in long-term power purchase agreements (PPAs)', 'Diversified mix of hydro (Karcham Wangtoo), wind, solar, and thermal assets', 'Strong promoter execution track record within the industrial JSW Group'],
        ['High financial leverage incurred during aggressive renewable capex build-outs', 'Seasonal generation fluctuations in hydroelectric and wind assets', 'Valuation premium elevates stock price drawdown risk during market corrections']
    )
])

# =============================================================================
# D. Consumer Goods and Retail (13 stocks)
# =============================================================================
stocks.extend([
    make_stock(
        'itc', 'ITC Limited', 'ITC',
        'Large-Cap Diversified FMCG & Hotels', 'Medium', 4, 485.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'Consumer powerhouse with dominant monopoly in legal cigarettes, surging non-cigarette FMCG brand portfolio (Aashirvaad, Sunfeast, Bingo), and hotel demerger value unlocking.',
        'Steady cigarette cash flows funding high-growth food FMCG scaling, hotel demerger, and attractive dividend yield.',
        ['Exceptional pricing power and high operating margins in core cigarette business delivering massive cash flows', 'Scale FMCG food brand portfolio generating over Rs 20,000 Crore in annual consumer spend', 'High dividend yield (~3.5%) backed by fortress net cash balance sheet and RoE > 28%'],
        ['Tobacco taxation increases and regulatory risks (GST council cess revisions)', 'FMCG non-cigarette segment operating margins still maturing compared to established pure-play peers', 'Market rotations into high-beta cyclicals can lead to periods of stock price consolidation']
    ),
    make_stock(
        'hindustan-unilever', 'Hindustan Unilever Limited', 'HINDUNILVR',
        'Large-Cap Essential FMCG Leader', 'Medium', 4, 2420.0, '> 5 Years',
        '11.5% - 14.5% CAGR', '5Y Historical CAGR',
        'India’s largest FMCG corporation touching 9 out of 10 households daily, leading in home care (Surf Excel, Rin), beauty & personal care (Dove, Lifebuoy), and foods (Horlicks, Knorr).',
        'Long-term compounding in per-capita consumer hygiene, premiumization, and deep rural distribution reach.',
        ['Unrivalled distribution reach penetrating over 9 million retail outlets across urban and rural India', 'Category leadership in 85% of its portfolio with strong pricing power and zero net debt', 'Consistent capital return with 100% dividend payout policy and exceptional RoCE (> 30%)'],
        ['Agricultural rural income slowdowns impact volume growth in mass market categories', 'Input commodity inflation (palm oil, crude derivatives) compressing gross margins', 'Direct equity market risks during consumer sector valuation de-rating']
    ),
    make_stock(
        'nestle-india', 'Nestlé India Limited', 'NESTLEIND',
        'Large-Cap Packaged Food & Nutrition', 'Medium', 4, 2380.0, '> 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR',
        'Packaged food giant dominating infant nutrition (Cerelac), instant noodles (Maggi), confectionery (KitKat), and coffee (Nescafé) with formidable pricing power.',
        'Urban convenience foods adoption, rural RURBAN project expansion, and coffee culture growth.',
        ['Near-monopoly market shares in instant noodles (~60%) and infant cereal nutrition (~70%)', 'Exceptional return on equity (RoE > 100%) supported by asset-light manufacturing and high brand equity', 'RURBAN distribution expansion driving penetration into tier-2/3/4 semi-urban markets'],
        ['Raw material cost spikes in dairy milk, coffee beans, and wheat flour', 'Intense consumer food safety scrutiny and regulatory compliance standards', 'Premium valuation multiples make the stock sensitive to quarterly volume growth misses']
    ),
    make_stock(
        'britannia-industries', 'Britannia Industries Limited', 'BRITANNIA',
        'Large-Cap Bakery & Foods FMCG', 'Medium', 4, 5450.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'India’s premier bakery food company commanding over 33% biscuit market share (Good Day, Marie Gold, NutriChoice), expanding into dairy, cakes, and snacking.',
        'Packaged biscuit premiumization, rural direct distribution expansion, and dairy cheese JV growth.',
        ['Iconic consumer brand recall and leadership across sweet, semi-sweet, and health biscuit segments', 'Direct distribution footprint reaching over 2.8 million retail outlets', 'Strong operating profit margins (~18%) and consistent return on capital (RoCE > 40%)'],
        ['Wheat, sugar, and palm oil commodity cost inflation pressuring gross profit margins', 'Intense competition from regional bakery players and multinational snacks companies', 'Stock market risk during FMCG sector corrections']
    ),
    make_stock(
        'tata-consumer-products', 'Tata Consumer Products Limited', 'TATACONSUM',
        'Large-Cap Branded Food & Beverages', 'Medium', 5, 1060.0, '> 5 Years',
        '13.5% - 16.5% CAGR', '5Y Historical CAGR',
        'FMCG arm of the Tata Group combining Tata Tea, Tata Salt, Sampann pulses, Soulfull snacks, and strategic acquisitions (Ching’s Secret, Organic India).',
        'Branded staples conversion from unorganized markets, health & wellness foods, and Tata Starbucks JV expansion.',
        ['National leadership in branded tea and vacuum evaporated iodized salt (Tata Salt market share > 38%)', 'High-growth portfolio expansion through acquisitions (Capital Foods Ching’s and Organic India)', 'Fast-growing Tata Starbucks retail joint venture scaling premium cafe locations across India'],
        ['Raw tea commodity auction price volatility and international beverage demand softness in the UK', 'Integration costs and margin gestation in newly acquired businesses', 'Equity valuation multiples require sustained double-digit revenue growth']
    ),
    make_stock(
        'godrej-consumer-products', 'Godrej Consumer Products Limited', 'GODREJCP',
        'Large-Cap Personal & Home Care FMCG', 'Medium', 5, 1240.0, '> 5 Years',
        '13.0% - 16.0% CAGR', '5Y Historical CAGR',
        'Leading emerging-markets FMCG player dominating household insecticides (Goodknight, HIT), hair colour (Godrej Expert), and personal wash (Cinthol), with scale operations in Indonesia and Africa.',
        'Household pest control penetration, hair care premiumization, and simplified supply chain restructuring.',
        ['Dominant market share in household insecticides across India with innovative low-cost liquid vaporizers', 'Strong footprint across fast-growing consumer markets in Indonesia and Africa', 'Ongoing portfolio simplification and divestment of non-core low-margin international assets'],
        ['Currency depreciation and macroeconomic volatility in African markets (Nigeria, Kenya)', 'Erratic monsoon patterns impacting household insecticide seasonal consumption', 'Equity market risk during consumer sector valuation resets']
    ),
    make_stock(
        'dabur-india', 'Dabur India Limited', 'DABUR',
        'Large-Cap Ayurvedic & Natural Healthcare', 'Medium', 4, 530.0, '> 5 Years',
        '12.0% - 14.5% CAGR', '5Y Historical CAGR',
        'World’s largest Ayurvedic and natural healthcare company with 140-year legacy, dominating Ayurvedic medicines (Chyawanprash, Honitus), hair care (Amla), and fruit juices (Real).',
        'Consumer shift toward natural herbal wellness, rural penetration, and healthcare OTC products.',
        ['Unrivalled brand trust and intellectual property in Ayurvedic healthcare and natural personal care', 'Market leadership in packaged fruit juices (Real market share > 60%)', 'Consistent dividend track record and zero net debt balance sheet'],
        ['High exposure to rural consumer sentiment (~47% of domestic sales from rural India)', 'Seasonal dependency on winter for healthcare products and summer for beverages', 'Market risk typical of defensive large-cap equities']
    ),
    make_stock(
        'marico', 'Marico Limited', 'MARICO',
        'Large-Cap Consumer Products', 'Medium', 4, 635.0, '> 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR',
        'Consumer products major dominating coconut hair oils (Parachute), premium refined edible oils (Saffola), and fast-growing digital-first direct-to-consumer food brands.',
        'Copra deflation tailwinds, Saffola health foods scaling (oats, peanut butter), and digital D2C brand compounding.',
        ['Monopoly market share (> 62%) in branded coconut hair oil (Parachute)', 'High brand equity in heart-healthy edible oils and healthy breakfast foods (Saffola)', 'Strong international presence across Bangladesh, South East Asia, and the Middle East'],
        ['Copra raw material commodity price volatility directly impacting gross profit margins', 'Slower urban demand recovery in premium edible oil segments', 'Currency risks in overseas emerging market subsidiaries']
    ),
    make_stock(
        'avenue-supermarts-dmart', 'Avenue Supermarts Limited (DMart)', 'DMART',
        'Large-Cap Organized Value Retail', 'High', 6, 4150.0, '> 5 Years',
        '15.0% - 18.5% CAGR', '5Y Historical CAGR',
        'India’s most profitable organized grocery supermarket chain, operating over 370 stores on an ownership real estate model with lowest operating costs and Everyday Low Prices (EDLP).',
        'Unorganized to organized modern grocery retail transition, new store cluster additions, and DMart Ready e-commerce scaling.',
        ['Lowest retail operating cost structure globally supported by store property ownership model', 'High inventory turnover and strong supplier bargaining power delivering lowest consumer prices', 'Huge structural runway: organized grocery retail accounts for less than 10% of total Indian retail'],
        ['Intense competition from quick-commerce 10-minute delivery apps in dense metro clusters', 'Capital-intensive real estate land acquisition limits rapid store opening acceleration', 'Premium valuation multiples elevate stock price sensitivity to quarterly store addition numbers']
    ),
    make_stock(
        'trent', 'Trent Limited', 'TRENT',
        'Large-Cap Fashion & Lifestyle Retail', 'High', 7, 7150.0, '3 - 5 Years',
        '17.0% - 22.0% CAGR', '5Y Historical CAGR',
        'Retail star of the Tata Group revolutionizing Indian fast fashion through Zudio (ultra-affordable trendy apparel) and Westside, delivering phenomenal store unit economics and like-for-like sales growth.',
        'Explosive nationwide Zudio store rollout, proprietary private label fast fashion, and Star Bazaar grocery JV expansion.',
        ['Zudio is India’s fastest-growing retail concept with unmatched unit economics and 15-day inventory turns', '100% private-label fashion portfolio generating high gross margins (> 45%)', 'World-class supply chain enabling immediate translation of global fashion trends to retail stores at Rs 299-999 price points'],
        ['High valuation multiples leave zero margin for any quarterly revenue or store addition slowdown', 'Rapid nationwide expansion increases store operational oversight and lease liability commitments', 'High stock price beta during broader market corrections']
    ),
    make_stock(
        'titan-company', 'Titan Company Limited', 'TITAN',
        'Large-Cap Jewellery & Lifestyle', 'Medium', 5, 3480.0, '> 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR',
        'Tata Group lifestyle giant dominating organized jewellery retail (Tanishq, Mia, CaratLane), watches (Titan, Fastrack), and eyewear, capturing formalization of gold jewellery.',
        'Shift from unorganized jewelers to trusted hallmarked Tanishq stores, wedding jewellery demand, and international NRI store expansion.',
        ['Unrivalled consumer trust in gold purity and hallmark craftsmanship under the Tata brand umbrella', 'Continuous market share gains from local jewelers driven by statutory hallmarking and transparent exchange policies', 'CaratLane acquisition provides dominant leadership in fast-growing modern studded diamond jewellery'],
        ['High gold bullion spot price spikes can temporarily dampen consumer jewellery volume demand', 'Customs import duty revisions and gold price hedging volatility', 'Direct equity market risks during consumer discretionary corrections']
    ),
    make_stock(
        'asian-paints', 'Asian Paints Limited', 'ASIANPAINT',
        'Large-Cap Decorative Coatings & Home Decor', 'Medium', 5, 2780.0, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR',
        'India’s dominant decorative paint manufacturer holding over 50% market share, with proprietary tinted automated dealer network and expanding home decor solutions.',
        'Indian housing renovation, repainting cycles, tier-2/3/4 real estate completion, and waterproofing products.',
        ['Unmatched supply chain and dealer tinting machine network present in over 75,000 paint retail counters', 'Best-in-class brand recall and multi-decade track record of high return on capital (RoCE > 30%)', 'Integrated home decor ecosystem offering modular kitchens, bath fittings, and lighting'],
        ['Intense competitive entry from deep-pocketed conglomerates (Birla Opus) pressuring industry gross margins', 'Crude oil derivative raw material cost spikes (solvents, titanium dioxide)', 'Sensitivity to real estate construction slowdowns']
    ),
    make_stock(
        'varun-beverages', 'Varun Beverages Limited', 'VBL',
        'Large-Cap Beverage Bottling Franchise', 'High', 6, 610.0, '3 - 5 Years',
        '16.0% - 19.5% CAGR', '5Y Historical CAGR',
        'PepsiCo’s second-largest bottling franchisee globally outside the US, manufacturing and distributing carbonated soft drinks (Pepsi, Mountain Dew, Sting) and juices (Tropicana) across India and Africa.',
        'Explosive energy drink growth (Sting), summer beverage demand, deep rural chilling equipment rollouts, and African market expansion (BevCo).',
        ['Exclusive long-term bottling franchise relationship with PepsiCo across 90%+ of Indian territory', 'Sting energy drink disrupted the mass beverage market, driving record volume expansion and margins', 'Strategic African acquisitions (South Africa, DRC) unlocking massive demographic growth corridors'],
        ['Erratic summer weather or prolonged unseasonal rainfall can heavily impact peak quarterly volumes', 'High capital expenditure incurred in continuous plant greenfield expansions and chilling assets', 'High valuation multiples make the stock volatile during consumer discretionary selloffs']
    )
])

print(f"Added Sectors C & D. Total stocks: {len(stocks)}")

# Save intermediate progress
stocks_path = os.path.join(root_dir, 'app', 'services', 'catalogue', 'stocks.py')
with open(stocks_path, 'w', encoding='utf-8') as f:
    f.write('"""\nExpanded Indian Stocks Catalogue across 9 Major Sectors for MoneyLeak.\n"""\n')
    f.write('from typing import Dict, Any, List\n\n')
    f.write('STOCKS_CATALOGUE: List[Dict[str, Any]] = ')
    pprint.pprint(stocks, stream=f, indent=4, width=120)
    f.write('\n')

print(f"Saved {len(stocks)} stocks.")
